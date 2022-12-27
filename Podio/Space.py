from dataclasses import dataclass
from .Interface import Interface
from .App import App
from .Widget import Widget
from .Files import File
from typing import List, Union, NoReturn
from collections import UserDict

class Space(UserDict):

    def __init__(self, interface: Interface, data: dict):
        super().__init__(data)

        self.interface = interface
        self._widget_params = {
            "interface": self.interface,
            "ref_id": self["space_id"],
            "ref_type": "space"
        }

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

        return await App.get_app_by_space(self.interface, self["space_id"])

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

    async def get_widgets(self):
        return await Widget.list_widgets(**self._widget_params)

    async def add_widget(self, widget_type: str, title: str, config: dict):
        return await Widget.add_widget(widget_type=widget_type, title=title, config=config,
                                 **self._widget_params)

    async def list_files(self) -> list[File]:
        return await File.list_space_files(self.interface, self["space_id"])

    async def add_member(self, role: str, message: str, users: Union[list[int], int, "User", list["User"]] = None,
                         profiles: Union[int, list[int]] = None, mails: Union[list[str], str] = None,
                         external_contacts: dict = None, item: int= None, invite_context: str = None) -> NoReturn:
        """
        Adds a member or members to a space.

        At least one of "users", "profiles", "mails", or "external_contacts" must be filled

        :param role: The Role to give to the Added user.  Can be one of "light", "regular", "admin"
        :param message: The custom message used to invite the user
        :param users: The Users to invite.  Can be a list or single entry of ID(s), or User Object(s)
        :param profiles: The profiles to invite. Can be a list or single entry of profile id(s)
        :param mails: the Email Address of people to invite. Can be a list or single entry of email(s)
        :param external_contacts: A dictionary of External contacts with their user IDs.  See Example Below.
        :param item: If permission is being given to an item instead of the Entire workspace, specify the item here. If
                     Specified, Permission will only be given to that item.
        :param invite_context: An optional custom string indicating where the user was when he/she invited the user(s).
        :return: No Return

        external contacts example:
        {
            LINKED_ACCOUNT_ID: [
                EXTERNAL CONTACT,
                EXTERNAL CONTACT
            ],
            ...
        }
        """

        payload = {"message": message}
        roles = ["light", "regular", "admin"]
        if role not in roles:
            raise Exception(f"\"role\" should one one of the following: {', '.join(roles)}")
        else:
            payload.update({"role": role})

        if users is not None and not isinstance(users, list):
            if not isinstance(users, int):
                payload.update({"users": [users["user_id"]]})
            else:
                payload.update({"users": [users]})
        elif users is not None and not isinstance(users[0], int):
            payload.update({"users": [user["user_id"] for user in users]})

        if profiles is not None:
            payload.update({"profiles": profiles if isinstance(profiles, list) else [profiles]})

        if mails is not None:
            payload.update({"mails": mails if isinstance(mails, list) else [mails]})

        if external_contacts is not None:
            payload.update({"external_contacts": external_contacts})

        if item is not None:
            payload.update({"context_ref_type": "item",
                            "context_ref_id": item})

        if invite_context is not None:
            payload.update({"invite_context": invite_context})

        await self.interface.call(f"/space/{self['space_id']}/member",
                                  method="POST",
                                  json=payload)
