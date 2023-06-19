import json
import requests
import ssl
import logging
from requests.exceptions import ReadTimeout
from websocket import create_connection
from websocket._exceptions import WebSocketTimeoutException

from .sense_api import *
from .sense_exceptions import *


class Senseable(SenseableBase):
    def set_ssl_context(self, ssl_verify, ssl_cafile):
        """Create or set the SSL context. Use custom ssl verification, if specified."""
        if not ssl_verify:
            self.s.verify = False
        elif ssl_cafile:
            self.s.verify = ssl_cafile

    def authenticate(self, username, password, ssl_verify=True, ssl_cafile=""):
        auth_data = {"email": username, "password": password}

        # Create session
        self.s = requests.session()
        self.set_ssl_context(ssl_verify, ssl_cafile)

        # Get auth token
        try:
            response = self.s.post(
                API_URL + "authenticate", auth_data, timeout=self.api_timeout
            )
        except Exception as e:
            raise Exception("Connection failure: %s" % e)

        # check MFA code required
        if response.status_code == 401:
            data = response.json()
            if "mfa_token" in data:
                self._mfa_token = data["mfa_token"]
                raise SenseMFARequiredException(data["error_reason"])

        # check for 200 return
        if response.status_code != 200:
            raise SenseAuthenticationException(
                "Please check username and password. API Return Code: %s"
                % response.status_code
            )

        self.set_auth_data(response.json())

    def validate_mfa(self, code):
        mfa_data = {
            "totp": code,
            "mfa_token": self._mfa_token,
            "client_time:": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        # Get auth token
        try:
            response = self.s.post(
                API_URL + "authenticate/mfa", mfa_data, timeout=self.api_timeout
            )
        except Exception as e:
            raise Exception("Connection failure: %s" % e)

        # check for 200 return
        if response.status_code != 200:
            raise SenseAuthenticationException(
                "Please check username and password. API Return Code: %s"
                % response.status_code
            )

        self.set_auth_data(response.json())

    # Update the realtime data
    def update_realtime(self, callback):
        # rate limit API calls
        # if (
        #     self._realtime
        #     and self.rate_limit
        #     and self.last_realtime_call + self.rate_limit > time()
        # ):
        #     return self._realtime
        url = WS_URL % (self.sense_monitor_id, self.sense_access_token)
        self.get_realtime_stream(callback)

    def get_realtime_stream(self, callback):
        """Reads realtime data from websocket
        Continues until loop broken"""
        ws = 0
        url = WS_URL % (self.sense_monitor_id, self.sense_access_token)
        startTime = time()
        try:
            ws = create_connection(
                url, timeout=self.wss_timeout, sslopt={"cert_reqs": ssl.CERT_NONE}
            )
            logging.info("created web socket connection")
            while True:  # hello, features, [updates,] data
                #logging.debug(ws.recv())
                result = json.loads(ws.recv())
                if result.get("type") == "realtime_update":
                    data = result["payload"]
                    self.set_realtime(data)
                    callback()
                    # yield data
                if (time() >= startTime + 60):
                    ws.ping()
                    logging.info("PING")
                    startTime = time()
        except:
            print("caught exception")
            #logging.debug(ws.recv())
            #logging.exception('')
            if ws:
                ws.close()
                print("close websocket")
                logging.warning("Close Websocket")
            #callback(True)
            #raise SenseAPITimeoutException("API websocket timed out")
            

    def get_trend_data(self, scale, dt=None):
        if scale.upper() not in valid_scales:
            raise Exception("%s not a valid scale" % scale)
        if not dt:
            dt = datetime.utcnow()
        self._trend_data[scale] = self.api_call(
            "app/history/trends?monitor_id=%s&scale=%s&start=%s"
            % (self.sense_monitor_id, scale, dt.strftime("%Y-%m-%dT%H:%M:%S"))
        )

    def update_trend_data(self, dt=None):
        for scale in valid_scales:
            self.get_trend_data(scale, dt)

    def api_call(self, url, payload={}):
        try:
            return self.s.get(
                API_URL + url,
                headers=self.headers,
                timeout=self.api_timeout,
                params=payload,
            ).json()
        except ReadTimeout:
            raise SenseAPITimeoutException("API call timed out")

    def get_discovered_device_names(self):
        # lots more info in here to be parsed out
        json = self.api_call("app/monitors/%s/devices" % self.sense_monitor_id)
        self._devices = [entry["name"] for entry in json]
        return self._devices

    def get_discovered_device_data(self):
        return self.api_call("monitors/%s/devices" % self.sense_monitor_id)

    def always_on_info(self):
        # Always on info - pretty generic similar to the web page
        return self.api_call(
            "app/monitors/%s/devices/always_on" % self.sense_monitor_id
        )

    def get_monitor_info(self):
        # View info on your monitor & device detection status
        return self.api_call("app/monitors/%s/status" % self.sense_monitor_id)

    def get_device_info(self, device_id):
        # Get specific informaton about a device
        return self.api_call(
            "app/monitors/%s/devices/%s" % (self.sense_monitor_id, device_id)
        )

    def get_monitor_data(self):
        # Get monitor overview info
        json = self.api_call("app/monitors/%s/overview" % self.sense_monitor_id)
        if "monitor_overview" in json and "monitor" in json["monitor_overview"]:
            self._monitor = json["monitor_overview"]["monitor"]
        return self._monitor

    def get_all_usage_data(self, payload={"n_items": 30}):
        """Gets usage data by device

        Args:
            payload (dict, optional): known params are:
                n_items: the number of items to return
                device_id: limit results to a specific device_id
                prior_to_item:. date in format YYYY-MM-DDTHH:MM:SS.mmmZ
                rollup: ?

                Defaults to {'n_items': 30}.

        Returns:
            dict: usage data
        """
        # lots of info in here to be parsed out
        return self.api_call("users/%s/timeline" % (self.sense_user_id), payload)
