from .Interface import Interface
from dataclasses import dataclass


@dataclass
class Flow:
    interface: Interface
    data: dict

    def __post_init__(self):
        self.__dict__.update(data)

    @classmethod
    async def get_flows(cls, interface: Interface, ref_type: str, ref_id: int):
        """
        Gets the flows associated with the reference

        :param ref_type: should be of type app
        :param ref_id: should be the id of the referencing type
        :return: a list of flows associated with the reference
        """

        endpoint = f"/{ref_type}/{ref_id}"

        response = await interface.call(endpoint)
        response = await response.json()

        return [Flow(interface, data) for data in response]