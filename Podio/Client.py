from .Interface import Interface
from .Organization import Organization


class Client:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str = None, username: str = None,
                 password: str = None):
        self.interface = Interface(client_secret, client_id, refresh_token, username, password)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close(exc_type, exc_val, exc_tb)

    async def close(self, exc_type, exc_val, exc_tb):
        await self.interface.close(exc_type, exc_val, exc_tb)

    async def get_org(self, url_label):
        return await Organization.get_org(url_label, self.interface)
