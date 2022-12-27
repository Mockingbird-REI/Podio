from .Interface import Interface
from collections import UserDict
from typing import Union

class Member(UserDict):
    def __init__(self, interface: Interface, data: dict):
        super().__init__(data)
        self.interface = interface

    @classmethod
    def get_members_from_space(cls, interface, space: Union[int, "Space"]) -> list["Member"]:
        """
        Retrieves a list of members from the given space

        :param interface: The interface used to interact with podio
        :param space: The Space in question.  Can either be a space_id or Space Object
        :return: a list of Member objects representing users and their relationship with the space
        """

        if not isinstance(space, int):
            space_id = space["space_id"]
        else:
            space_id = space

        response = await interface.call(f"/space/{space_id}/member/")
        data = await response.json()

        return [cls(interface, member) for member in data]