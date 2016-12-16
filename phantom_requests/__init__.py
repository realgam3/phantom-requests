__title__ = 'phantom-requests'
__version__ = '0.0.1'
__build__ = 0x000001
__author__ = 'Tomer Zait (RealGame)'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 Tomer Zait'

from requests import auth
from requests import cookies
from .sessions import session, Session
from requests import Request, Response, PreparedRequest
from . import utils
