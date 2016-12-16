from . import sessions


def request(method, url, **kwargs):
    with sessions.Session() as session:
        return session.request(method=method, url=url, **kwargs)


def get(url, params=None, **kwargs):
    return request('GET', url, params=params, **kwargs)


def options(url, **kwargs):
    return request('OPTIONS', url, **kwargs)


def head(url, **kwargs):
    return request('HEAD', url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    return request('POST', url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    return request('PUT', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return request('PATCH', url, data=data, **kwargs)


def delete(url, **kwargs):
    return request('DELETE', url, **kwargs)
