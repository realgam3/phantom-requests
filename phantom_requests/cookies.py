from requests.cookies import *


class PhantomJSCookieJar(RequestsCookieJar):
    def __init__(self, driver, policy=None):
        super(PhantomJSCookieJar, self).__init__(policy)
        self.driver = driver

    def set(self, name, value, **kwargs):
        if value is None:
            self.driver.delete_cookie(name)
            remove_cookie_by_name(self, name, domain=kwargs.get('domain'), path=kwargs.get('path'))
            return

        if isinstance(value, Morsel):
            c = morsel_to_cookie(value)
        else:
            c = create_cookie(name, value, **kwargs)

        self.driver.add_cookie({
            'name': c.name,
            'value': c.name,
            'domain': c.domain,
            'path': c.path,
            'secure': c.secure,
            'expires': c.expires,
            'httponly': getattr(c, 'HttpOnly', False)
        })
        self.set_cookie(c)
        return c
