from .Interface import Interface
from dataclasses import dataclass
from typing import List
from .Space import Space


@dataclass
class Organization:
    url_label: str
    interface: Interface
    data: dict

    def __post_init__(self):
        self.__dict__.update(self.data)

    @classmethod
    async def get_org(cls, url_label: str, interface: Interface) -> "Organization":
        """
        Creates an Organization Object
        :param url_label: Then Name of the org as found in the URL
        :param interface: The interface object
        :return: An Organization object representing the target Organization
        """
        params = {
            "url": f"https://podio.com/{url_label}"
        }

        response = await interface.call("/org/url", params=params)
        response = await response.json()

        return Organization(url_label, interface, response)

    async def get_spaces(self) -> List[Space]:
        """
        Gets the Spaces for the Organization

        :return: a list of spaces for the org
        """

        return await Space.get_space_by_org(self.interface, self.org_id)

    async def new_space(self, name: str, privacy: str = "closed", auto_join: bool = False, new_app_post: bool = False,
                        new_member_post: bool = False) -> Space:
        """
        Creates a new space in the Organization specified

        :param name: The Name of the App
        :param privacy: Privacy level of the space, "open" or "closed
        :param auto_join: Should new employees auto join this space?
        :param new_app_post: Should post when an app is added?
        :param new_member_post: should post when a new member is added?

        :return: Returns a Space object representing the newly created Space
        """

        return await Space.new_space(self.interface, self.org_id, name, privacy, auto_join, new_app_post,
                                     new_member_post)
