# -*- coding: utf-8 -*-

import re
from os import path
from json import dumps
from selenium import webdriver
from requests import Request, Response, PreparedRequest
from requests.exceptions import ProxyError, ConnectionError

from . import utils
from .cookies import PhantomJSCookieJar, RequestsCookieJar
from .structures import CaseInsensitiveDict, Proxies, Headers

try:
    from Cookie import SimpleCookie
except ImportError:
    # Python3
    from http.cookies import SimpleCookie

EXECUTE_PHANTOM_JS = "executePhantomJS"
REQUEST_PHANTOM_JS = "requestPhantomJS"
PAGE_PHANTOM_JS = "pagePhantomJS"
GHOST_DRIVER_PATH = path.abspath(path.join(path.dirname(__file__), 'ghostdriver', 'src', 'main.js'))


class PhantomJS(webdriver.PhantomJS):
    def __init__(self, executable_path="phantomjs",
                 port=0, desired_capabilities=webdriver.DesiredCapabilities.PHANTOMJS,
                 service_args=None, service_log_path=None):
        port = port or utils.free_port()
        service_args = service_args or []
        service_args.insert(0, GHOST_DRIVER_PATH)
        service_args.insert(1, '--port=%d' % port)
        super(PhantomJS, self).__init__(executable_path, port, desired_capabilities, service_args, service_log_path)
        self.command_executor._commands[EXECUTE_PHANTOM_JS] = ('POST', '/session/$sessionId/phantom/execute')
        self.command_executor._commands[REQUEST_PHANTOM_JS] = ('POST', '/session/$sessionId/phantom/request')
        self.command_executor._commands[PAGE_PHANTOM_JS] = ('GET', '/session/$sessionId/phantom/page')

    def execute_phantomjs(self, script, *args):
        converted_args = list(args)
        return self.execute(EXECUTE_PHANTOM_JS,
                            {'script': script, 'args': converted_args})['value']

    def request(self, url, method='GET', data=None, headers=None, encoding='utf8'):
        settings = {
            'operation': method,
            'data': data,
            'headers': dict(headers),
            'encoding': encoding
        }
        return self.execute(REQUEST_PHANTOM_JS,
                            {'url': url, 'settings': settings})['value']

    def get_page(self):
        return self.execute(PAGE_PHANTOM_JS)['value']


class Session(object):
    def __init__(self, executable_path="phantomjs", port=0):
        self.desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
        self.driver = PhantomJS(
            executable_path=executable_path,
            desired_capabilities=self.desired_capabilities,
            service_log_path=path.devnull,
            port=port,
        )
        self.auth = None
        self.params = {}
        self.verify = True
        self._headers = utils.default_headers(self.driver)
        self._proxies = Proxies(self.driver)
        self._cookies = PhantomJSCookieJar(self.driver)

    def close(self):
        self.driver.quit()

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
        return self._proxies

    @proxies.setter
    def proxies(self, *args, **kwargs):
        self._proxies = Proxies(self.driver, *args, **kwargs)

    @property
    def cookies(self):
        for cookie in self.driver.get_cookies():
            cookie['rest'] = {
                'HttpOnly': cookie.pop('httponly', None)
            }
            cookie['expires'] = cookie.pop('expiry', None)
            cookie['update_driver'] = False
            self._cookies.set(**cookie)
        return self._cookies

    @staticmethod
    def _extract_response(page, encoding='utf8'):
        history = []
        set_cookies = []
        res = None
        for i, url in enumerate(page['history']):
            resource = page['resources'].pop(0)
            while resource['request']['url'] != url:
                resource = page['resources'].pop(0)

            if resource['error']:
                return resource['error'], None

            request = resource['request']
            req = PreparedRequest()
            req.method = request['method'].encode(encoding)
            req.url = request['url'].encode(encoding)

            # Set Request Headers
            req.headers = CaseInsensitiveDict()
            for header in request['headers']:
                req.headers[header['name'].encode(encoding)] = header['value'].encode(encoding)

            # Set Request Cookies
            req._cookies = RequestsCookieJar()
            if set_cookies:
                if 'Cookie' not in req.headers:
                    req.headers['Cookie'] = ""
                else:
                    set_cookies.insert(0, '')
                req.headers['Cookie'] += "; ".join(set_cookies)

            if 'Cookie' in req.headers:
                cookies = SimpleCookie()
                cookies.load(req.headers['Cookie'])
                for key, cookie in cookies.items():
                    req._cookies.set(key, cookie.value)

            req.body = request.get('postData', None)
            if req.body:
                req.body = req.body.encode(encoding)

            response = resource['endReply'] or resource['startReply']
            res = Response()
            res.encoding = encoding
            res.url = response['url'].encode(encoding)
            res.status_code = response['status']
            for header in response['headers']:
                res.headers[header['name'].encode(encoding)] = header['value'].encode(encoding)
                if header['name'] == 'Set-Cookie':
                    set_cookies.append(res.headers[header['name']].rsplit(';', 1)[0])

            res.history = list(history)
            res.request = req

            history.append(res)

        res._content = re.sub(
            (
                '<html><head></head><body>'
                '<pre style="word-wrap: break-word; white-space: pre-wrap;">(.*?)</pre>'
                '</body></html>'
            ),
            r'\1',
            page['content'],
            flags=re.DOTALL
        ).encode(encoding)

        return None, res

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

        # Set Proxies
        if proxies is not None:
            req_proxies = Proxies(self.driver, self.proxies)
            req_proxies.update(proxies)

        prep_headers = CaseInsensitiveDict(self.headers)
        prep_headers.update(headers or {})

        cookies_to_restore = []
        url_parsed = utils.urlparse(url)
        prep_cookies = self.cookies.get_dict(domain=url_parsed.netloc)
        prep_cookies.update(cookies or {})
        if cookies is not None:
            for name, value in cookies.items():
                cookies_to_restore.append(self.driver.get_cookie(name))
                self.driver.execute_phantomjs("this.addCookie({})".format(dumps(
                    {'name': name, 'value': value, 'domain': url_parsed.netloc}
                )))

        prep_params = params or {}
        prep_params.update(self.params)

        req = Request(method, url, prep_headers, files, data, prep_params,
                      self.auth or auth, prep_cookies, hooks, json)
        prep = req.prepare()

        self.driver.request(prep.url, prep.method, prep.body, prep.headers)
        error, res = self._extract_response(self.driver.get_page())

        # Clean
        if proxies is not None:
            self.proxies.update()

        if cookies is not None:
            for name, _ in cookies.items():
                self.driver.delete_cookie(name)
            for cookie in cookies_to_restore:
                if not cookie:
                    continue
                self.driver.execute_phantomjs("this.addCookie({})".format(dumps(cookie)))

        if error:
            if proxies and error['errorCode'] == 1:
                raise ProxyError(error['errorString'])
            raise ConnectionError(error['errorString'])

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
