import json
from requests import Session as RequestsSession
from phantom_requests import Session as PhantomJSSession

if __name__ == '__main__':
    # print 'PhantomJS:'
    with PhantomJSSession() as session:
        session.headers.update({'test1': 'test1', 'test2': 'test2'})
        print 'Session Headers: %s' % json.dumps(dict(session.headers), indent=4)

        # Add Request Params, Request Headers.
        res = session.get('http://httpbin.org/get', headers={'a': 'a'}, params={'test': 'test'})
        print 'Result Content: %s' % res.content

        # Add Request Proxies.
        res = session.get('http://httpbin.org/ip', proxies={'http': '127.0.0.1:8080'})
        print 'Result JSON: %s' % json.dumps(res.json(), indent=4)

    print '________________________________________________________\n'

    print 'Requests:'
    with RequestsSession() as session:
        session.headers.update({'test1': 'test1', 'test2': 'test2'})
        print session.headers
        print 'Session Headers: %s' % json.dumps(dict(session.headers), indent=4)

        # Add Request Params, Request Headers.
        res = session.get('http://httpbin.org/get', headers={'a': 'a'}, params={'test': 'test'})
        print 'Result Content: %s' % res.content

        # Add Request Proxies.
        res = session.get('http://httpbin.org/ip', proxies={'http': '127.0.0.1:8080'})
        print 'Result JSON: %s' % json.dumps(res.json(), indent=4)
