from .Interface import Interface
from .Organization import Organization
from .App import App
from .Files import File


class Client:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str = None, username: str = None,
                 password: str = None):
        self.interface = Interface(client_secret, client_id, refresh_token, username, password)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.interface.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        await self.interface.close()

    async def get_org(self, url_label):
        return await Organization.get_org(url_label, self.interface)

    async def get_app_by_id(self, app_id):
        return await App.get_app_by_id(self.interface, app_id)

    async def copy_file(self, file_id):
        return await File.copy_file(self.interface, file_id)
