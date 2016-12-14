import re
from os import path
from selenium import webdriver
from requests import Request, Response

from .stractures import Proxies, Headers

EXECUTE_PHANTOM_JS = "executePhantomJS"


class PhantomJS(webdriver.PhantomJS):
    def __init__(self, *args, **kwargs):
        super(PhantomJS, self).__init__(*args, **kwargs)
        self.command_executor._commands[EXECUTE_PHANTOM_JS] = ('POST', '/session/$sessionId/phantom/execute')

    def execute_phantomjs(self, script, *args):
        converted_args = list(args)
        return self.execute(EXECUTE_PHANTOM_JS,
                            {'script': script, 'args': converted_args})['value']


class Session(object):
    def __init__(self, executable_path="phantomjs"):
        self.desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
        self.driver = PhantomJS(
            executable_path=executable_path,
            desired_capabilities=self.desired_capabilities,
            service_log_path=path.devnull
        )
        self._headers = Headers(self.driver)
        self._proxies = Proxies(self.driver)

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, *args, **kwargs):
        self._headers = Headers(self.driver, *args, **kwargs)

    @property
    def proxies(self):
        return self._headers

    @proxies.setter
    def proxies(self, *args, **kwargs):
        self._proxies = Proxies(self.driver, *args, **kwargs)

    def request(self, method, url,
                params=None,
                data=None,
                headers=None,
                cookies=None,
                files=None,
                auth=None,
                timeout=None,
                allow_redirects=True,
                proxies=None,
                hooks=None,
                stream=None,
                verify=None,
                cert=None,
                json=None):
        method_upper = method.upper()

        # Set Headers
        if headers:
            req_headers = Headers(self.driver, self.headers)
            req_headers.update(headers)

        # Set Proxies
        if proxies:
            req_proxies = Proxies(self.driver, self.proxies)
            req_proxies.update(proxies)

        req = Request(method, url, headers, files, data, params, auth, cookies, hooks, json)
        prep = req.prepare()

        if method_upper == 'GET':
            self.driver.get(prep.url)
        else:
            raise NotImplementedError

        # Prepare Response
        res = Response()
        res_content = re.sub(
            (
                '<html><head></head><body>'
                '<pre style="word-wrap: break-word; white-space: pre-wrap;">(.*?)</pre>'
                '</body></html>'
            ),
            r'\1',
            self.driver.page_source,
            flags=re.DOTALL
        )
        res._content = res_content.encode('utf-8')
        res.encoding = 'utf-8'
        res.request = prep

        # Clean
        if headers:
            self.headers.update()

        if proxies:
            self.proxies.update()

        return res

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def close(self):
        return self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


def session(*args, **kwargs):
    return Session(*args, **kwargs)
