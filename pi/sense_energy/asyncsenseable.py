import asyncio
import json
import ssl

import aiohttp
import websockets

from .sense_api import *
from .sense_exceptions import *


class ASyncSenseable(SenseableBase):
    def __init__(
        self,
        username=None,
        password=None,
        api_timeout=API_TIMEOUT,
        wss_timeout=WSS_TIMEOUT,
        client_session=None,
        ssl_verify=True,
        ssl_cafile="",
    ):
        """Init the ASyncSenseable object."""
        self._client_session = client_session or aiohttp.ClientSession()

        super().__init__(
            username=username,
            password=password,
            api_timeout=api_timeout,
            wss_timeout=wss_timeout,
            ssl_verify=ssl_verify,
            ssl_cafile=ssl_cafile,
        )

    def set_ssl_context(self, ssl_verify, ssl_cafile):
        """Create or set the SSL context. Use custom ssl verification, if specified."""
        if not ssl_verify:
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        elif ssl_cafile:
            self.ssl_context = ssl.create_default_context(cafile=ssl_cafile)
        else:
            self.ssl_context = ssl.create_default_context()

    async def authenticate(self, username, password, ssl_verify=True, ssl_cafile=""):
        auth_data = {"email": username, "password": password}
        self.set_ssl_context(ssl_verify, ssl_cafile)

        # Get auth token
        async with self._client_session.post(
            API_URL + "authenticate", timeout=self.api_timeout, data=auth_data
        ) as resp:

            # check MFA code required
            if resp.status == 401:
                data = await resp.json()
                if "mfa_token" in data:
                    self._mfa_token = data["mfa_token"]
                    raise SenseMFARequiredException(data["error_reason"])

            # check for 200 return
            if resp.status != 200:
                raise SenseAuthenticationException(
                    "Please check username and password. API Return Code: %s"
                    % resp.status
                )

            # Build out some common variables
            self.set_auth_data(await resp.json())

    async def validate_mfa(self, code):
        mfa_data = {
            "totp": code,
            "mfa_token": self._mfa_token,
            "client_time:": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # Get auth token
        async with self._client_session.post(
            API_URL + "authenticate/mfa", timeout=self.api_timeout, data=mfa_data
        ) as resp:

            # check for 200 return
            if resp.status != 200:
                raise SenseAuthenticationException(f"API Return Code: {resp.status}")

            # Build out some common variables
            self.set_auth_data(await resp.json())

    # Update the realtime data for asyncio
    async def update_realtime(self):
        # rate limit API calls
        if (
            self._realtime
            and self.rate_limit
            and self.last_realtime_call + self.rate_limit > time()
        ):
            return self._realtime
        self.last_realtime_call = time()
        await self.async_realtime_stream(single=True)

    async def async_realtime_stream(self, callback=None, single=False):
        """Reads realtime data from websocket"""
        url = WS_URL % (self.sense_monitor_id, self.sense_access_token)
        # hello, features, [updates,] data
        async with websockets.connect(url, ssl=self.ssl_context) as ws:
            while True:
                try:
                    message = await asyncio.wait_for(
                        ws.recv(), timeout=self.wss_timeout
                    )
                except asyncio.TimeoutError as ex:
                    raise SenseAPITimeoutException("API websocket timed out") from ex

                result = json.loads(message)
                if result.get("type") == "realtime_update":
                    data = result["payload"]
                    self.set_realtime(data)
                    if callback:
                        callback(data)
                    if single:
                        return
                elif result.get("type") == "error":
                    data = result["payload"]
                    raise SenseWebsocketException(data["error_reason"])

    async def get_realtime_future(self, callback):
        """Returns an async Future to parse realtime data with callback"""
        await self.async_realtime_stream(callback)

    async def api_call(self, url, payload={}):
        timeout = aiohttp.ClientTimeout(total=self.api_timeout)
        try:
            async with self._client_session.get(
                API_URL + url, headers=self.headers, timeout=timeout, data=payload
            ) as resp:
                # check for 200 return
                if resp.status != 200:
                    raise SenseAuthenticationException(f"API Return Code: {resp.status}")

                return await resp.json()
        except asyncio.TimeoutError as ex:
            # timed out
            raise SenseAPITimeoutException("API call timed out") from ex

    async def get_trend_data(self, scale, dt=None):
        if scale.upper() not in valid_scales:
            raise Exception("%s not a valid scale" % scale)
        if not dt:
            dt = datetime.utcnow()
        json = self.api_call(
            "app/history/trends?monitor_id=%s&scale=%s&start=%s"
            % (self.sense_monitor_id, scale, dt.strftime("%Y-%m-%dT%H:%M:%S"))
        )
        self._trend_data[scale] = await json

    async def update_trend_data(self, dt=None):
        for scale in valid_scales:
            await self.get_trend_data(scale, dt)

    async def get_monitor_data(self):
        json = await self.api_call("app/monitors/%s/overview" % self.sense_monitor_id)
        if "monitor_overview" in json and "monitor" in json["monitor_overview"]:
            self._monitor = json["monitor_overview"]["monitor"]
        return self._monitor

    async def get_discovered_device_names(self):
        # lots more info in here to be parsed out
        json = self.api_call("app/monitors/%s/devices" % self.sense_monitor_id)
        self._devices = await [entry["name"] for entry in json]
        return self._devices

    async def get_discovered_device_data(self):
        json = self.api_call("monitors/%s/devices" % self.sense_monitor_id)
        return await json
