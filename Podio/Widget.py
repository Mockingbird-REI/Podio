"""
For Classes that use Widgets:
 - Space
 - App
 - Organization
 - User

Refer to Widget Configuration Here: https://developers.podio.com/doc/widgets
"""
import logging

from collections import UserDict
from .Interface import Interface
from pprint import pprint as pp
from .Tools import Tools


class Widget(UserDict):

    QUOTED_LIST = '\", \"'

    # Widget types and configuration properties
    WIDGET_TYPES = {
        "text": ["text"],
        "image": ["file_id"],
        "link": ["links"],
        "tag_cloud": ["limit"],
        "calculation": ["app_id", "app_link", "calculation", "unit"],
        "tasks": ["kind", "limit"],
        "events": ["limit"],
        "profiles": ["limit"],
        "apps": ["limit"],
        "app_view": ["view_id", "limit"],
        "contacts": ["limit"],
        "files": ["limit"]
    }

    def __init__(self, interface: Interface, ref_type: str, ref_id: int, data: dict):
        super().__init__(data)
        self.tools = Tools(interface)

        self.interface = interface
        self.ref_type = ref_type
        self.ref_id = ref_id
        self.base_url = f"/widget/{ref_type}/{ref_id}"

    @classmethod
    async def list_widgets(cls, interface: Interface, ref_type: str, ref_id: int) -> list["Widget"]:
        """ Returns a list of widgets

        :param interface: The interface to interact with the Podio API
        :param ref_type: the reference type of the object being queried
        :param ref_id:
        """
        response = await interface.call(f"/widget/{ref_type}/{ref_id}")

        widget_list = list()
        for widget in await response.json():
            widget_list.append(Widget(interface, ref_type, ref_id, widget))

        return widget_list

    @classmethod
    async def add_widget(cls, interface: Interface, ref_type: str, ref_id: int, widget_type: str, title: str, config: dict):
        """

        :param interface:
        :param ref_type:
        :param ref_id:
        :param widget_type:
        :param title:
        :param config:
        :return:

        When adding images, ensure that the images are not already used or they will cause an error.  You may need to
        re embed an already embeded image file.
        """
        if widget_type not in cls.WIDGET_TYPES:
            raise Exception(f"Not a valid widget type.  Valid widget types are \"{cls.QUOTED_LIST.join(cls.WIDGET_TYPES)}\"")
        elif not all([widget_prop in config for widget_prop in cls.WIDGET_TYPES[widget_type]]):
            print(f"ERROR: {config.keys()} {cls.WIDGET_TYPES[widget_type]}")
            error_string = (f"Widget Config must contain the following properties: "
                            f"\"{cls.QUOTED_LIST.join(cls.WIDGET_TYPES[widget_type])}\"")
            raise Exception(error_string)

        # Remove configs that are not defined
        rm_config = []
        for prop in config:
            if config[prop] is None:
                rm_config.append(prop)

        [config.pop(prop) for prop in rm_config]

        # Finally make the request
        payload = {
            "type": widget_type,
            "title": title,
            "config": config
        }
        pp(payload)

        response = await interface.call(f"/widget/{ref_type}/{ref_id}/",
                                        method="POST",
                                        json=payload)

        resp_data = await response.json()

        widget_data = {
            "widget_id": resp_data["widget_id"],
            "ref": {
                "type": ref_type,
                "id": ref_id
            },
            "type": widget_type,
            "title": title,
            "config": config
        }

        return Widget(interface, ref_type, ref_id, widget_data)

    @classmethod
    async def get_widget(cls, interface: Interface, widget_id: int):
        response = await interface.call(f"/widget/{widget_id}")
        resp_data = await response.json()

        return Widget(interface,
                      resp_data["ref"]["id"],
                      resp_data["ref"]["type"],
                      resp_data)


    async def refresh(self):
        response = await self.get_widget(self.interface, self["widget_id"])

        self.data.update(response.data)

    async def delete(self):
        await self.interface.call(f"/widget/{self['widget_id']}", method="DELETE")