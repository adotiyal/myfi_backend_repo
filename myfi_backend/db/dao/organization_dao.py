from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from myfi_backend.db.dependencies import get_db_session
from myfi_backend.db.models.organization_model import Organization


class OrganizationDAO:
    """Class for accessing organizations table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Organization:
        """
        Create a new organization.

        :param name: name of the organization.
        :param description: description of the organization.
        :return: the created organization.
        """
        organization = Organization(name=name, description=description)
        self.session.add(organization)
        await self.session.commit()
        return organization

    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Organization]:
        """
        Get all organizations with limit/offset pagination.

        :param limit: limit of organizations.
        :param offset: offset of organizations.
        :return: stream of organizations.
        """
        query = select(Organization).limit(limit).offset(offset)
        raw_organizations = await self.session.execute(query)
        return list(raw_organizations.scalars().fetchall())

    async def get_by_id(self, organization_id: int) -> Optional[Organization]:
        """
        Get an organization by ID.

        :param organization_id: ID of the organization.
        :return: the organization, or None if not found.
        """
        query = select(Organization).where(Organization.id == organization_id)
        raw_organization = await self.session.execute(query)
        organization = raw_organization.scalars().first()
        return organization if organization else None

    async def update(
        self,
        organization_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Organization]:
        """
        Update an organization by ID.

        :param organization_id: ID of the organization.
        :param name: new name of the organization.
        :param description: new description of the organization.
        :return: the updated organization, or None if not found.
        """
        organization = await self.get_by_id(organization_id)
        if organization:
            if name:
                organization.name = name
            if description:
                organization.description = description
            await self.session.commit()
        return organization

    async def delete(self, organization_id: int) -> Optional[Organization]:
        """
        Delete an organization by ID.

        :param organization_id: ID of the organization.
        :return: the deleted organization, or None if not found.
        """
        organization = await self.get_by_id(organization_id)
        if organization:
            await self.session.delete(organization)
            await self.session.commit()
        return organization
