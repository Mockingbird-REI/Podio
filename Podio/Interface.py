from aiohttp import ClientSession, ClientResponse, ClientResponseError
import logging
from pprint import pprint as pp

log = logging.getLogger()


class Interface:
    def __init__(self, client_secret: str, client_id: str, refresh_token: str = None, username: str = None,
                 password: str = None):
        self.base_url = "https://api.podio.com"
        self.session: ClientSession = ClientSession()
        self.client_secret = client_secret
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.username = username
        self.password = password

    async def close(self):
        await self.session.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def authenticate(self):
        endpoint = "/oauth/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        if self.refresh_token is None:
            if not all([self.username, self.password]):
                log.error("Please provide a refresh token or username and password.")
                raise Exception("No Auth Credentials")

            params.update({
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
            })

            response = await self.call(endpoint, "POST", auth_call=True, params=params)
            response = await response.json()
            self.refresh_token = response['refresh_token']

        else:
            params.update({
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            })

            response = await self.call(endpoint, "POST", auth_call=True, params=params)
            response = await response.json()

        self.session = ClientSession(
            headers={"Authorization": f"OAuth2 {response['access_token']}"})

    async def call(self, endpoint: str, method: str = "GET", auth_call:bool = False, **kwargs) -> ClientResponse:
        """ Makes calls to podio

        :param endpoint: The endpoint to call
        :param method: The method to use
        :param kwargs: Other arguments for ClientSession calls
        :return: a Client Response Object
        """
        if not self.session.headers.get("Authorization") and not auth_call:
            await self.authenticate()

        url = f"{self.base_url}{endpoint}"
        response = await self.session.request(method, url, **kwargs)

        await self.error_check(response)

        return response

    async def error_check(self, response: ClientResponse):
        try:
            response.raise_for_status()
        except ClientResponseError as e:
            data = await response.json()
            log.error(data["error_description"])

            await self.session.close()
            raise e
