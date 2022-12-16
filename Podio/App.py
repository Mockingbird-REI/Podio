from .Interface import Interface
from dataclasses import dataclass
from typing import List, Union
from pprint import pprint as pp
from .Flow import Flow
import logging


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

    async def export_items(self):
        """
        Exports Items from the Space in an XLSX format

        :return: A file Like Object formatted as XLSX
        """

        response = await self.interface.call(f"/item/app/{self.app_id}/xlsx")

        return await response.json()

    async def filter_items(self):
        """
        Gilters items and returns the matching

        :return: a list of items related to the filters
        """

        response = await self.interface.call(f"/item/app/{self.data['app_id']}/filter/", method="POST")

        return await response.json()

    async def add_item(self, item: dict):
        """
        Adds an Item to the app

        :param item: A dictionary Representation of the Item to add
        :return: The title and item id as a dictionary
        """
        post_item = {}
        for field in item:
            try:
                self_field = [self_field for self_field in self.data["fields"] if field in self_field["label"]][0]
            except IndexError:
                logging.error(f"No Matching field for {field}")
                raise Exception("No Matching Field")

            if field == "Description":
              post_item.update({"title": item[field]})
            elif self_field["type"] == "embed":
                post_item.update({self_field["external_id"]: await self._process_embed(*item[field])})
            else:
                post_item.update({self_field["external_id"]: item[field]})

        response = await self.interface.call(f"/item/app/{self.data['app_id']}",
                                             method="POST",
                                             json={"fields": post_item})

        return await response.json()

    async def _process_embed(self, embed_type, embed_value):
        if embed_type == "link":
            if isinstance(embed_value, list):
                return [await self._embed_link(value) for value in embed_value]
            else:
                return [await self._embed_link(embed_value)]

        # TODO: Write logic for the rest of the embeds

    async def copy_item(self, item):
        item_copy = {}
        for field in item["fields"]:
            if isinstance(field['values'], list):
                item_copy.update({field["label"]: [value for value in field["values"]]})
            else:
                item_copy.update({field["label"]: [field["values"]]})

        return await self.add_item(item_copy)

    async def _embed_link(self, url):
        response = await self.interface.call("/embed/",
                                             method="POST",
                                             json={"url":url})

        return await response.json()
