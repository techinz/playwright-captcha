import httpx

DEFAULT_BASE_URL = "https://api.peak.fo"


class AsyncPeakClient:
    """Minimal async client for the Peak captcha-solving API (peak.fo)"""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 180.0):
        """
        :param api_key: Peak API key (format 'pk_...')
        :param base_url: Peak API base URL
        :param timeout: Request timeout in seconds (solves can take a few seconds)
        """

        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    @property
    def _headers(self) -> dict:
        return {'X-API-Key': self.api_key, 'Content-Type': 'application/json'}

    async def solve(self, task_type: str, url: str, sitekey: str = None, proxy: str = None,
                    cdata: str = None, action: str = None, pagedata: str = None) -> str:
        """
        Send a solve request and return the token

        :param task_type: Peak task type, e.g. 'turnstiletask'
        :param url: URL of the page the captcha is on
        :param sitekey: Turnstile site key
        :param proxy: Proxy the solve runs through (format 'http://user:pass@host:port')
        :param cdata: Optional Turnstile cData
        :param action: Optional Turnstile action
        :param pagedata: Optional Turnstile chlPageData

        :return: The solved token

        :raises RuntimeError: If Peak reports a failure or returns no token
        """

        payload = {'task_type': task_type, 'url': url}
        for key, value in (('sitekey', sitekey), ('proxy', proxy), ('cdata', cdata),
                           ('action', action), ('pagedata', pagedata)):
            if value:
                payload[key] = value

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f'{self.base_url}/solve', json=payload, headers=self._headers)
            data = response.json()

        if not data.get('success'):
            raise RuntimeError(data.get('error') or 'Peak solve failed')

        token = (data.get('data') or {}).get('token')
        if not token:
            raise RuntimeError('Peak response did not contain a token')

        return token

    async def balance(self) -> float:
        """ Get account balance """

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f'{self.base_url}/balance', headers=self._headers)
            data = response.json()

        return float((data.get('data') or {}).get('balance', 0.0))
