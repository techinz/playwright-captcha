#!/usr/bin/env python3

import asyncio
import os
import time
from base64 import b64encode

import httpx

from .async_api import AsyncApiClient
from .exceptions.solver import ValidationException, NetworkException, TimeoutException, ApiException, \
    SolverExceptions


# it's just a changed version of the original 2captcha client

class AsyncCaptchaAI():
    def __init__(self,
                 apiKey,
                 softId=4580,
                 callback=None,
                 defaultTimeout=120,
                 recaptchaTimeout=600,
                 pollingInterval=10,
                 server='ocr.captchaai.com',
                 extendedResponse=None):

        self.API_KEY = apiKey
        self.soft_id = softId
        self.callback = callback
        self.default_timeout = defaultTimeout
        self.recaptcha_timeout = recaptchaTimeout
        self.polling_interval = pollingInterval
        self.api_client = AsyncApiClient(post_url=str(server))
        self.max_files = 9
        self.exceptions = SolverExceptions
        self.extendedResponse = extendedResponse

    async def recaptcha(self, sitekey, url, version='v2', enterprise=0, **kwargs):
        '''Wrapper for solving recaptcha (v2, v3).

        Parameters
        _______________
        sitekey : str
            Value of sitekey parameter you found on page.
        url : str
            Full URL of the page where you see the reCAPTCHA.
        domain : str, optional
            Domain used to load the captcha: google.com or recaptcha.net. Default: google.com.
        invisible : int, optional
            1 - means that reCAPTCHA is invisible. 0 - normal reCAPTCHA. Default: 0.
        version : str, optional
            v3 — defines that you're sending a reCAPTCHA V3. Default: v2.
        enterprise : str, optional
            1 - defines that you're sending reCAPTCHA Enterpise. Default: 0.
        action : str, optional
            Value of action parameter you found on page. Default: verify.
        score : str, only for v3, optional
            The score needed for resolution. Currently, it's almost impossible to get token with score higher than 0.3.
            Default: 0.4.
        data-s : str, only for v2, optional
            Value of data-s parameter you found on page. Curenttly applicable for Google Search and other Google services.
        cookies : str, only for v2, optional
            Your cookies that will be passed to our worker who solve the captha. We also return worker's cookies in the
            response if you use json=1. Format: KEY:Value, separator: semicolon, example: KEY1:Value1;KEY2:Value2;
        userAgent : str, only for v2, optional
            Your userAgent that will be passed to our worker and used to solve the captcha.
        softId : int, optional
            ID of software developer. Developers who integrated their software with CaptchaAI get reward: 10% of
            spendings of their software users.
        callback : str, optional
            URL for pingback (callback) response that will be sent when captcha is solved. URL should be registered on
            the server. More info here https://captchaai.com/api-docs.php#solving_recaptchav2
        proxy : dict, optional
            {'type': 'HTTPS', 'uri': 'login:password@IP_address:PORT'}.
        '''

        params = {
            'googlekey': sitekey,
            'url': url,
            'method': 'userrecaptcha',
            'version': version,
            'enterprise': enterprise,
            **kwargs,
        }

        result = await self.solve(timeout=self.recaptcha_timeout, **params)
        return result

    async def solve(self, timeout=0, polling_interval=0, **kwargs):
        '''Sends captcha, receives result.

        Parameters
        __________
        timeout : float

        polling_interval : int

        **kwargs : dict
            all captcha params

        Returns

        result : string
        '''

        id_ = await self.send(**kwargs)
        result = {'captchaId': id_}

        if self.callback is None:
            timeout = float(timeout or self.default_timeout)
            sleep = int(polling_interval or self.polling_interval)

            code = await self.wait_result(id_, timeout, sleep)

            if self.extendedResponse == True:
                new_code = {
                    key if key != 'request' else 'code': value
                    for key, value in code.items()
                    if key != 'status'
                }
                result.update(new_code)
            else:
                result.update({'code': code})

            return result

    async def wait_result(self, id_, timeout, polling_interval):
        max_wait = time.time() + timeout

        while time.time() < max_wait:
            try:
                return await self.get_result(id_)
            except NetworkException:
                await asyncio.sleep(polling_interval)

        raise TimeoutException(f'timeout {timeout} exceeded')

    async def get_method(self, file):
        if not file:
            raise ValidationException('File required')

        if not '.' in file and len(file) > 50:
            return {'method': 'base64', 'body': file}

        if file.startswith('http'):
            async with httpx.AsyncClient() as client:
                img_resp = await client.get(file)
                if img_resp.status_code != 200:
                    raise ValidationException(f'File could not be downloaded from url: {file}')
                return {'method': 'base64', 'body': b64encode(img_resp.content).decode('utf-8')}

        if not os.path.exists(file):
            raise ValidationException(f'File not found: {file}')

        return {'method': 'post', 'file': file}

    async def send(self, **kwargs):
        """This method can be used for manual captcha submission

        Parameters
        _________
        method : str
            The name of the method must be found in the documentation https://captchaai.com/api-docs.php
        kwargs: dict
            All captcha params
        Returns

        """
        params = self.default_params(kwargs)
        params = self.rename_params(params)

        params, files = self.check_hint_img(params)

        response = await self.api_client.in_(files=files, **params)

        if not response.startswith('OK|'):
            raise ApiException(f'cannot recognize response {response}')

        return response[3:]

    async def get_result(self, id_):
        import json
        """This method can be used for manual captcha answer polling.

        Parameters
        __________
        id_ : str
            ID of the captcha sent for solution
        Returns

        answer : text
        """
        if self.extendedResponse == True:
            response = await self.api_client.res(key=self.API_KEY, action='get', id=id_, json=1)
            response_data = json.loads(response)

            if response_data.get("status") == 0:
                raise NetworkException

            if not response_data.get("status") == 1:
                raise ApiException(f'Unexpected status in response: {response_data}')

            return response_data
        else:
            response = await self.api_client.res(key=self.API_KEY, action='get', id=id_)

            if response == 'CAPCHA_NOT_READY':
                raise NetworkException

            if not response.startswith('OK|'):
                raise ApiException(f'cannot recognize response {response}')

            return response[3:]

    async def balance(self):
        '''Get my balance

        Returns

        balance : float
        '''
        response = await self.api_client.res(key=self.API_KEY, action='getbalance')
        return float(response)

    async def report(self, id_, correct):
        '''Report of solved captcha: good/bad.

        Parameters
        __________
        id_ : str
            captcha ID

        correct : bool
            True/False

        Returns
            None.

        '''
        rep = 'reportgood' if correct else 'reportbad'
        await self.api_client.res(key=self.API_KEY, action=rep, id=id_)
        return

    def rename_params(self, params):
        replace = {
            'caseSensitive': 'regsense',
            'minLen': 'min_len',
            'maxLen': 'max_len',
            'minLength': 'min_len',
            'maxLength': 'max_len',
            'hintText': 'textinstructions',
            'hintImg': 'imginstructions',
            'url': 'pageurl',
            'score': 'min_score',
            'text': 'textcaptcha',
            'rows': 'recaptcharows',
            'cols': 'recaptchacols',
            'previousId': 'previousID',
            'canSkip': 'can_no_answer',
            'apiServer': 'api_server',
            'softId': 'soft_id',
            'callback': 'pingback',
            'datas': 'data-s',
        }

        new_params = {
            v: params.pop(k)
            for k, v in replace.items() if k in params
        }

        proxy = params.pop('proxy', '')
        proxy and new_params.update({
            'proxy': proxy['uri'],
            'proxytype': proxy['type']
        })

        new_params.update(params)

        return new_params

    def default_params(self, params):
        params.update({'key': self.API_KEY})

        callback = params.pop('callback', self.callback)
        soft_id = params.pop('softId', self.soft_id)

        if callback: params.update({'callback': callback})
        if soft_id: params.update({'softId': soft_id})

        self.has_callback = bool(callback)

        return params

    def extract_files(self, files):
        if len(files) > self.max_files:
            raise ValidationException(
                f'Too many files (max: {self.max_files})')

        not_exists = [f for f in files if not (os.path.exists(f))]

        if not_exists:
            raise ValidationException(f'File not found: {not_exists}')

        files = {f'file_{e + 1}': f for e, f in enumerate(files)}
        return files

    def check_hint_img(self, params):
        hint = params.pop('imginstructions', None)
        files = params.pop('files', {})

        if not hint:
            return params, files

        if not '.' in hint and len(hint) > 50:
            params.update({'imginstructions': hint})
            return params, files

        if not os.path.exists(hint):
            raise ValidationException(f'File not found: {hint}')

        if not files:
            files = {'file': params.pop('file', {})}

        files.update({'imginstructions': hint})

        return params, files
