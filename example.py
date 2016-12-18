import json
import functools
from requests.auth import HTTPBasicAuth
from requests.exceptions import ProxyError
from requests import Session as RequestsSession
from phantom_requests import Session as PhantomJSSession

if __name__ == '__main__':
    for name, session_class in {'PhantomJS': functools.partial(PhantomJSSession, port=8910),
                                'Requests': RequestsSession}.items():
        print '\n%s:' % name
        print '________________________________________________________\n'

        with session_class() as session:
            session.headers.update({'Header1': 'Value1', 'Header2': 'Value2'})
            print 'Session Headers: %s' % json.dumps(dict(session.headers), indent=4)

            # Add Request Params, Request Headers.
            res = session.get(
                'http://httpbin.org/get',
                headers={'header_name': 'header_value'},
                params={'param_name': 'param_value'}
            )
            print 'GET Result Content: %s' % res.content
            print 'GET Request Headers: %s' % json.dumps(dict(res.request.headers), indent=4)
            print res.headers

            # Add Request Proxies.
            try:
                res = session.post(
                    'http://httpbin.org/post',
                    proxies={'http': '127.0.0.1:8888'},
                    json={'json_name': 'json_value'},
                    params={'param_name': 'param_value'},
                    auth=HTTPBasicAuth('auth_user', 'auth_pass'),
                    cookies={'cookie_name': 'cookie_value'}
                )
                print 'POST Result JSON: %s' % json.dumps(res.json(), indent=4)
            except ProxyError as ex:
                print 'For That Test You Will Need Proxy That Listen On Port 8888:'
                print 'That Exception Is Fine: %s\n' % ex

            print "Cookies Tricks:"
            session.get('http://httpbin.org/cookies/set?k2=v2&k1=v1', cookies={'a': 'b'})
            print session.cookies.get_dict()
            res = session.get('http://httpbin.org/cookies', cookies={'a': 'b'})
            print res.request._cookies.get_dict()
            print res.cookies.get_dict()
            print session.cookies.get_dict()
