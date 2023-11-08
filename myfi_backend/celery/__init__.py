"""This module initializes the Celery app for the myfi_backend.

It imports the Celery
instance from the tasks module and sets the __all__ variable to expose the celery
instance to other modules.

Attributes:
    celery: The Celery instance for the MyFi backend.
"""

from myfi_backend.celery.tasks import celery

__all__ = ("celery",)
