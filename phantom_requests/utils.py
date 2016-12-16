from requests.utils import urlparse
from selenium.webdriver.common.utils import free_port

from . import __version__
from .structures import Headers


def default_user_agent(name="phantom-requests"):
    return '%s/%s' % (name, __version__)


def default_headers(driver):
    return Headers(driver, {
        'User-Agent': default_user_agent(),
        'Accept-Encoding': ', '.join(('gzip', 'deflate')),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,*",
    })
