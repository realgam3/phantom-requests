import re
import json
from requests.structures import CaseInsensitiveDict


class CaseInsensitiveOnChangeDict(CaseInsensitiveDict):
    def __init__(self, callback=lambda: None, data=None, **kwargs):
        super(CaseInsensitiveOnChangeDict, self).__init__(data=data, **kwargs)
        self.__callback = callback
        if data:
            self.callback()

        self.clear = self.callback_wrapper(self.clear)
        self.pop = self.callback_wrapper(self.pop)
        self.popitem = self.callback_wrapper(self.popitem)
        self.update = self.callback_wrapper(self.update)
        self.__delitem__ = self.callback_wrapper(self.__delitem__)
        self.__setitem__ = self.callback_wrapper(self.__setitem__)

    @property
    def callback(self):
        return self.__callback

    @callback.setter
    def callback(self, value):
        self.__callback = value
        self.callback()

    def callback_wrapper(self, func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            self.callback()
            return res

        return wrapper


class Headers(CaseInsensitiveOnChangeDict):
    def __init__(self, driver, data=None, **kwargs):
        self.driver = driver
        super(Headers, self).__init__(self.set_headers, data, **kwargs)

    def set_headers(self):
        self.driver.execute_phantomjs("this.customHeaders={};".format(json.dumps(dict(self))))


class Proxies(CaseInsensitiveOnChangeDict):
    def __init__(self, driver, data=None, **kwargs):
        self.driver = driver
        super(Proxies, self).__init__(self.set_proxies, data, **kwargs)

    def set_proxies(self):
        proxy_re = re.compile(
            '^(?:(?P<un>\w+):(?P<pw>\w+)@)?(?P<host>\d{1,3}(?:\.\d{1,3}){3}):(?P<port>\d{1,5})$'
        )
        for proxy_type, proxy_str in self.items():
            proxy = proxy_re.search(self[proxy_type])
            if not re.match('^\w+$', proxy_type) or not proxy:
                continue

            self.driver.execute_phantomjs(
                "phantom.setProxy('{host}', {port}, '{type}', '{un}', '{pw}');".format(
                    type=proxy_type,
                    host=proxy.group('host'),
                    port=proxy.group('port'),
                    un=proxy.group('un') or '',
                    pw=proxy.group('pw') or '',
                )
            )

        if not self:
            self.driver.execute_phantomjs("phantom.setProxy('');")
