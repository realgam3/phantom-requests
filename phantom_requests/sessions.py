import re
from os import path
from selenium import webdriver
from requests import Request, Response
from selenium.webdriver.common.utils import free_port

from .structures import Proxies, Headers

EXECUTE_PHANTOM_JS = "executePhantomJS"
REQUEST_PHANTOM_JS = "requestPhantomJS"
GHOST_DRIVER_PATH = path.abspath(path.join(path.dirname(__file__), 'ghostdriver', 'main.js'))


class PhantomJS(webdriver.PhantomJS):
    def __init__(self, executable_path="phantomjs",
                 port=0, desired_capabilities=webdriver.DesiredCapabilities.PHANTOMJS,
                 service_args=None, service_log_path=None):
        port = port or free_port()
        service_args = service_args or []
        service_args.insert(0, GHOST_DRIVER_PATH)
        service_args.insert(1, '--port=%d' % port)
        super(PhantomJS, self).__init__(executable_path, port, desired_capabilities, service_args, service_log_path)
        self.command_executor._commands[EXECUTE_PHANTOM_JS] = ('POST', '/session/$sessionId/phantom/execute')
        self.command_executor._commands[REQUEST_PHANTOM_JS] = ('POST', '/session/$sessionId/phantom/request')

    def execute_phantomjs(self, script, *args):
        converted_args = list(args)
        return self.execute(EXECUTE_PHANTOM_JS,
                            {'script': script, 'args': converted_args})['value']

    def request(self, url, method='GET', data=None):
        return self.execute(REQUEST_PHANTOM_JS,
                            {'url': url, 'method': method, 'data': data})['value']


class Session(object):
    def __init__(self, executable_path="phantomjs"):
        self.desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
        self.driver = PhantomJS(
            executable_path=executable_path,
            desired_capabilities=self.desired_capabilities,
            service_log_path=path.devnull
        )
        self._headers = Headers(self.driver, {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,*",
            "User-Agent": "phantom-requests/0.0.1"
        })
        self._proxies = Proxies(self.driver)

    def close(self):
        return self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

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

        # Set Headers
        req_headers = self.headers
        if headers:
            req_headers = Headers(self.driver, req_headers)
            req_headers.update(headers)

        # Set Proxies
        if proxies:
            req_proxies = Proxies(self.driver, self.proxies)
            req_proxies.update(proxies)

        req = Request(method, url, req_headers, files, data, params, auth, cookies, hooks, json)
        prep = req.prepare()
        req_headers.update(prep.headers)

        self.driver.request(prep.url, prep.method, prep.body)

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

    def options(self, url, **kwargs):
        return self.request('OPTIONS', url, **kwargs)

    def head(self, url, **kwargs):
        return self.request('HEAD', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.request('POST', url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.request('PUT', url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        return self.request('PATCH', url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)


def session(*args, **kwargs):
    return Session(*args, **kwargs)
