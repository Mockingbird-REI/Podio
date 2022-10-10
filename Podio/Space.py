from dataclasses import dataclass
from .Interface import Interface
from .App import App
from typing import List

@dataclass
class Space:
    interface: Interface
    data: dict

    def __post_init__(self):
        self.__dict__.update(self.data)

    @classmethod
    async def get_space_by_id(cls, interface: Interface, space_id: int) -> "Space":
        """
        Returns a Space Object

        :param interface: The interface to interact with Podio
        :param space_id: The ID of the space to retrieve
        :return: A Space Object
        """

        response = await interface.call(f"/space/{space_id}")

        return cls(interface, await response.json())

    @classmethod
    async def get_space_by_org(cls, interface: Interface, org_id: int) -> List["Space"]:
        """
        Returns an Async list of Space Objects

        :param interface: The interface to interact with Podio
        :param org_id: The ID of the org
        :return: a list of Space Objects
        """

        url = f"/space/org/{org_id}/"

        response = await interface.call(url)

        space_list = list()
        for space in await response.json():
            space_list.append(Space(interface, space))

        return space_list

    async def get_apps(self) -> List[App]:
        """
        Gets a list of the Apps in the space

        :return: a List of App objects
        """

        return await App.get_app_by_space(self.interface, self.space_id)

    @classmethod
    async def new_space(cls, interface: Interface, org_id: int, name: str, privacy: str = "closed",
                        auto_join: bool = False, new_app_post: bool = False, new_member_post: bool = False) -> "Space":
        """
        Creates a new space in the Organization specified
        :param interface: The interface to interact with Podio
        :param org_id: the ID of the org to create the new space in
        :param name: The Name of the App
        :param privacy: Privacy level of the space, "open" or "closed
        :param auto_join: Should new employees auto join this space?
        :param new_app_post: Should post when an app is added?
        :param new_member_post: should post when a new member is added?
        :return: Returns a Space object representing the newly created Space
        """

        endpoint = "/space/"

        json = {
            "org_id": org_id,
            "name": name,
            "privacy": privacy,
            "auto_join": auto_join,
            "new_app_post": new_app_post,
            "new_member_post": new_member_post
        }

        response = await interface.call(endpoint, method="POST", json=json)
        response = await response.json()
        space_id = response["space_id"]

        return await cls.get_space_by_id(interface, space_id)
