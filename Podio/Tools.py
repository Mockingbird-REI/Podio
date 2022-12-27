from .Interface import Interface

class Tools:
    def __init__(self, interface: Interface):
        self.interface = interface

    async def embed_link(self, link):
        response = await self.interface.call("/embed/",
                                             method="POST",
                                             json={"url": link})

        return await response.json()
