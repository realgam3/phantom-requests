import json
from requests import Session as RequestsSession
from phantom_requests import Session as PhantomJSSession

if __name__ == '__main__':
    print 'PhantomJS:'
    with PhantomJSSession() as session:
        session.headers.update({'test1': 'test1', 'test2': 'test2'})
        print 'Session Headers: %s' % json.dumps(dict(session.headers), indent=4)

        # Add Request Params, Request Headers.
        res = session.get('http://httpbin.org/get', headers={'a': 'a'}, params={'test': 'test'})
        print 'GET Result Content: %s' % res.content
        print 'GET Request Headers: %s' % json.dumps(dict(res.request.headers), indent=4)

        # Add Request Proxies.
        res = session.post('http://httpbin.org/post', proxies={'http': '127.0.0.1:8080'}, json={'test': 'test'})
        print 'POST Result JSON: %s' % json.dumps(res.json(), indent=4)

    print '________________________________________________________\n'

    print 'Requests:'
    with RequestsSession() as session:
        session.headers.update({'test1': 'test1', 'test2': 'test2'})
        print 'Session Headers: %s' % json.dumps(dict(session.headers), indent=4)

        # Add Request Params, Request Headers.
        res = session.get('http://httpbin.org/get', headers={'a': 'a'}, params={'test': 'test'})
        print 'GET Result Content: %s' % res.content
        print 'GET Request Headers: %s' % json.dumps(dict(res.request.headers), indent=4)

        # Add Request Proxies.
        res = session.post('http://httpbin.org/post', proxies={'http': '127.0.0.1:8080'}, json={'test': 'test'})
        print 'POST Result JSON: %s' % json.dumps(res.json(), indent=4)
