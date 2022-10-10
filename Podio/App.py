from .Interface import Interface
from dataclasses import dataclass
from typing import List, Union
from pprint import pprint as pp
from .Flow import Flow


@dataclass
class App:
    interface: Interface
    data: dict

    def __post_init__(self):
        self.__dict__.update(self.data)

    @classmethod
    async def get_app_by_space(cls, interface: Interface, space_id: int) -> List["App"]:
        """
        Returns a list of the apps in a space

        :param interface: The Interface to interact with podio
        :param space_id: the ID of the Space
        :return: a list of app objects
        """

        url = f"/app/space/{space_id}"
        response = await interface.call(url)

        app_list = list()
        for app in await response.json():
            app_data = await (await interface.call(f"/app/{app['app_id']}")).json()
            app_list.append(App(interface, app_data))

        return app_list

    @classmethod
    async def get_app_by_id(cls, interface: Interface, app_id: int) -> "App":
        """
        Gets the App in question

        :param interface: The interface to interact with podio
        :param app_id: The ID of the app in question
        :return: an App object
        """

        url = f"/app/{app_id}"

        response = await interface.call(url)
        response = await response.json()

        return App(interface, response)

    async def copy(self, space: Union["Space", int]) -> "App":
        """
        Copies an app to a space the API user has access to

        :param space: The Space to copy the App to.  Can be a space object or Space ID

        :return: a new app object represent the newly created app
        """

        if not isinstance(space, int):
            space = space.space_id

        json = {
            "space_id": space
        }

        response = await self.interface.call(f"/app/{self.app_id}/install", "POST", json=json)
        response = await response.json()
        new_app_id = response["app_id"]

        return await self.get_app_by_id(self.interface, new_app_id)

    async def get_flows(self):
        """
        Gets the flows associated with the App

        :return: A list of flow objects
        """

        return Flow.get_flows("app", self.app_id)

