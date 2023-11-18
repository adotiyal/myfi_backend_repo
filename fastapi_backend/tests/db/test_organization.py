import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_backend.db.dao.organization_dao import OrganizationDAO


@pytest.mark.anyio
async def test_organization_dao(dbsession: AsyncSession) -> None:
    """Test OrganizationDAO create, get_all, get_by_id, update, and delete."""
    # Create a new organization
    dao = OrganizationDAO(dbsession)
    organization = await dao.create(
        name="Test Organization",
        description="This is a test organization",
    )
    assert organization.id is not None
    assert organization.name == "Test Organization"
    assert organization.description == "This is a test organization"

    # Get all organizations
    organizations = await dao.get_all()
    assert len(organizations) == 1
    assert organizations[0].id == organization.id
    assert organizations[0].name == "Test Organization"
    assert organizations[0].description == "This is a test organization"

    # Get an organization by ID
    organization_by_id = await dao.get_by_id(organization.id)
    assert organization_by_id is not None
    assert organization_by_id.id == organization.id
    assert organization_by_id.name == "Test Organization"
    assert organization_by_id.description == "This is a test organization"

    # Update an organization
    updated_organization = await dao.update(
        organization.id,
        name="Updated Organization",
    )
    assert updated_organization is not None
    assert updated_organization.id == organization.id
    assert updated_organization.name == "Updated Organization"
    assert updated_organization.description == "This is a test organization"

    # Delete an organization
    deleted_organization = await dao.delete(organization.id)
    assert deleted_organization is not None
    assert deleted_organization.id == organization.id

    # Make sure the organization was deleted
    organization_by_id = await dao.get_by_id(organization.id)
    assert organization_by_id is None
