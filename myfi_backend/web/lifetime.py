from typing import Awaitable, Callable

from fastapi import FastAPI
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    TELEMETRY_SDK_LANGUAGE,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider
from prometheus_fastapi_instrumentator.instrumentation import (
    PrometheusFastApiInstrumentator,
)
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from myfi_backend.services.redis.lifetime import init_redis, shutdown_redis
from myfi_backend.settings import settings


def _setup_db(app: FastAPI) -> None:
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


def setup_opentelemetry(app: FastAPI) -> None:
    """
    Enables opentelemetry instrumentation.

    :param app: current application.
    """
    if not settings.opentelemetry_endpoint:
        return

    tracer_provider = TracerProvider(
        resource=Resource(
            attributes={
                SERVICE_NAME: "myfi_backend",
                TELEMETRY_SDK_LANGUAGE: "python",
                DEPLOYMENT_ENVIRONMENT: settings.environment,
            },
        ),
    )

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=settings.opentelemetry_endpoint,
                insecure=True,
            ),
        ),
    )

    excluded_endpoints = [
        app.url_path_for("health_check"),
        app.url_path_for("openapi"),
        app.url_path_for("swagger_ui_html"),
        app.url_path_for("swagger_ui_redirect"),
        app.url_path_for("redoc_html"),
        "/metrics",
    ]

    FastAPIInstrumentor().instrument_app(
        app,
        tracer_provider=tracer_provider,
        excluded_urls=",".join(excluded_endpoints),
    )
    RedisInstrumentor().instrument(
        tracer_provider=tracer_provider,
    )
    SQLAlchemyInstrumentor().instrument(
        tracer_provider=tracer_provider,
        engine=app.state.db_engine.sync_engine,
    )

    set_tracer_provider(tracer_provider=tracer_provider)


def stop_opentelemetry(app: FastAPI) -> None:
    """
    Disables opentelemetry instrumentation.

    :param app: current application.
    """
    if not settings.opentelemetry_endpoint:
        return

    FastAPIInstrumentor().uninstrument_app(app)
    RedisInstrumentor().uninstrument()
    SQLAlchemyInstrumentor().uninstrument()


def setup_prometheus(app: FastAPI) -> None:
    """
    Enables prometheus integration.

    :param app: current application.
    """
    PrometheusFastApiInstrumentator(should_group_status_codes=False).instrument(
        app,
    ).expose(app, should_gzip=True, name="prometheus_metrics")


def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        _setup_db(app)
        setup_opentelemetry(app)
        init_redis(app)
        setup_prometheus(app)
        pass  # noqa: WPS420

    return _startup


def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.db_engine.dispose()

        await shutdown_redis(app)
        stop_opentelemetry(app)
        pass  # noqa: WPS420

    return _shutdown
