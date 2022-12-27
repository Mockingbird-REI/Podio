from .Interface import Interface
from typing import IO, Union
from collections import UserDict
from uuid import uuid4
from aiohttp import FormData

class File(UserDict):
    def __init__(self, interface: Interface, data: dict):
        super().__init__(data)
        self.interface = interface

    @classmethod
    async def upload_file(cls, interface, file: Union[str, IO], file_name: str = None) -> "File":
        """ Uploads a file to Podio

        :param file: The File to upload to Podio. Can either be the content of a file or a file path.
        :param file_name: What to call the file.  Otherwise, a UUID will be created and used
        :return: an object representing the File
        """

        if isinstance(file, str):
            with open(file) as file:
                content = file.read()
        else:
            content = file

        data = FormData()
        data.add_field('file',
                       content,
                       filename=file_name if file_name else str(uuid4()))

        response = await interface.call("/file", data=data)

        return File(interface, data)

    async def copy(self):
        return await self.copy_file(self.interface, self["file_id"])

    @classmethod
    async def copy_file(cls, interface, file_id) -> "File":
        response = await interface.call(f"/file/{file_id}/copy",
                                        method="POST")
        response = await response.json()

        return await cls.get_file(interface, response["file_id"])

    @classmethod
    async def get_file(cls, interface, file_id) -> "File":
        response = await interface.call(f"/file/{file_id}")
        data = await response.json()

        return File(interface, data)

    @classmethod
    async def list_space_files(cls, interface: Interface, space_id: int, attached_to: str = None, file_type: str = None,
                               hosted_by: str = None, limit: int = 20, offset: int = 0, sort_by: str = "name",
                               sort_desc: bool = True) -> list["File"]:
        """
        Lists the files for a given space

        :param interface: The Interface object to interact with Podio
        :param space_id: The id of the space to get the files from
        :param attached_to: Filter: the  "item", "status", "task", or "space" the files are attached to
        :param file_type: Filter: file Type.  Can be one of ("image", "application", "video", "text", "audio")
        :param hosted_by: Filter: Who is the file hosted by. Can be one of
            ("podio", "google", "boxnet", "dropbox", "evernote", "live", "sharefile", "sugarsync", "yousendit")
        :param limit: The number of results to retrun per pagination
        :param offset: The offset for the request when using Pagination
        :param sort_by: Sort results by name or created on. Default: Name
        :param sort_desc: Sorty By Decending or Ascending Default Decending (True)
        :return: A list of files attachd to the space with the given parameters
        """

        exception_errors = []
        params = {}

        # Verify parameters
        attached_to_values = ("item", "status", "task", "space")
        if attached_to is not None and attached_to not in attached_to_values:
            exception_errors.append(f"\"attached_to\" should be one of: {', '.join(attached_to_values)}")
        elif attached_to is not None:
            params.update({"attached_to": attached_to})

        file_type_values = ("image", "application", "video", "text", "audio")
        if file_type is not None and file_type not in file_type_values:
            exception_errors.append(f"\"file_type\" should be one of: {', '.join(attached_to_values)}")
        elif file_type is not None:
            params.update({"filetype": file_type})

        hosted_by_values = ("podio", "google", "boxnet", "dropbox", "evernote", "live", "sharefile", "sugarsync",
                            "yousendit")
        if hosted_by is not None and hosted_by not in hosted_by_values:
            exception_errors.append(f"\"hosted_by\" should be one of: {', '.join(hosted_by_values)}")
        elif hosted_by is not None:
            params.update({"hosted_by": hosted_by})

        sort_by_values = ("name", "created_on")
        if sort_by not in sort_by_values:
            exception_errors.append(f"\"sort_by\" should be one of: {', '.join(sort_by_values)}")
        else:
            params.update({"sort_by": sort_by})

        # Make the Call
        params.update({"limit": limit,
                       "sort_desc": str(sort_desc),
                       "offset": offset})

        if exception_errors:
            raise Exception("\n".join(exception_errors))

        print(space_id)

        response = await interface.call(f"/file/space/{space_id}", params=params)

        return [cls(interface, data) for data in await response.json()]
