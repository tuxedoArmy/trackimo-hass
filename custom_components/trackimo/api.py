import json
import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)

class TrackimoApiClient:
    """Trackimo API client."""

    def __init__(self, username, password, hass, debug=False):
        """Initialize the client."""
        self.server_url = 'https://app.trackimo.com'
        self.client_id = '0431448f-644c-490d-bc58-76431c3618cd'
        self.client_secret = 'f157e0c54dd4ae7b925b536da2904679'
        self.redirect_uri = 'http://golandemo.com'
        self.username = username
        self.password = password
        self.hass = hass
        self.debug = debug # Keep debug for now, will remove later
        self.access_token = None
        self.account_id = None

    async def async_get_access_token(self):
        """Get access token."""
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server_url + '/api/internal/v2/user/login',
                                    headers={'Content-Type': 'application/json'},
                                    json={"username": self.username, "password": self.password}) as resp:
                if resp.status != 200:
                    _LOGGER.error("Login failed: %s", await resp.text())
                    return False
                cookies = resp.cookies

            async with session.get(self.server_url + '/api/v3/oauth2/auth',
                                   params={'client_id': self.client_id,
                                           'redirect_uri': self.redirect_uri,
                                           'response_type': 'code',
                                           'scope': 'locations,notifications,devices,accounts,settings,geozones'},
                                   cookies=cookies,
                                   allow_redirects=False) as resp:
                if resp.status != 302:
                    _LOGGER.error("Auth failed: %s", await resp.text())
                    return False
                headers = {k.lower(): v for k, v in resp.headers.items()}
                location = headers['location']
                code = location.split('=')[1]

            async with session.post(self.server_url + '/api/v3/oauth2/token',
                                    headers={'Content-Type': 'application/json'},
                                    json={'client_id': self.client_id,
                                          'client_secret': self.client_secret,
                                          'code': code},
                                    cookies=cookies) as resp:
                if resp.status != 200:
                    _LOGGER.error("Token exchange failed: %s", await resp.text())
                    return False
                
                response_json = await resp.json()
                if self.debug:
                    _LOGGER.debug("Access Token Response: %s", json.dumps(response_json, indent=2))

                self.access_token = response_json.get('access_token')
                return True

    async def async_get_user_details(self):
        """Get user details."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url + '/api/v3/user', headers={'Authorization': 'Bearer %s' % self.access_token}) as resp:
                response_json = await resp.json()
                if self.debug:
                    _LOGGER.debug("User Details Response: %s", json.dumps(response_json, indent=2))
                self.account_id = response_json.get('account_id')
                return response_json

    async def async_get_devices(self):
        """Get devices."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url + '/api/v3/accounts/%s/devices?limit=10&page=1' % self.account_id,
                                    headers={'Authorization': 'Bearer %s' % self.access_token}) as resp:
                response_json = await resp.json()
                if self.debug:
                    _LOGGER.debug("Devices List Response: %s", json.dumps(response_json, indent=2))
                return response_json

    async def async_get_device_last_location(self, device_id):
        """Get device last location."""
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server_url + '/api/v3/accounts/%s/locations/filter?limit=1' % self.account_id,
                                    json={"device_ids": [device_id]},
                                    headers={'Authorization': 'Bearer %s' % self.access_token,
                                             'Content-Type': 'application/json'}) as resp:
                if resp.status != 200:
                    _LOGGER.error("Get device last location failed: %s", await resp.text())
                    return None
                response_json = await resp.json()
                if self.debug:
                    _LOGGER.debug("Device Last Location Response: %s", json.dumps(response_json, indent=2))
                return response_json[0] if response_json else None