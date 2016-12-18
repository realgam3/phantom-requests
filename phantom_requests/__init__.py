__title__ = 'phantom-requests'
__version__ = '0.0.1'
__build__ = 0x000001
__author__ = 'Tomer Zait (RealGame)'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 Tomer Zait'

from requests import auth, exceptions, status_codes, models
from requests.models import Request, Response, PreparedRequest
from requests.status_codes import codes
from requests.exceptions import (
    RequestException, Timeout, URLRequired,
    TooManyRedirects, HTTPError, ConnectionError,
    FileModeWarning, ConnectTimeout, ReadTimeout
)

from . import utils
from .sessions import session, Session
from .api import request, get, head, post, patch, put, delete, options
