#!/usr/bin/env python

from setuptools import setup

setup(
    name='phantom-requests',
    version='0.0.1',
    description='Use PhantomJS As You Are Using Requests.',
    author='Tomer Zait (RealGame)',
    author_email='realgam3@gmail.com',
    packages=['phantom_requests'],
    package_data={
        'phantom_requests': [
            'ghostdriver/VERSION',
            'ghostdriver/*.*',
            'ghostdriver/src/*.*',
            'ghostdriver/src/request_handlers/*.*',
            'ghostdriver/src/third_party/*.*',
            'ghostdriver/src/third_party/webdriver-atoms/*.*',
        ]
    },
    install_requires=[
        'selenium >= 3.0.1',
        'requests >= 2.11.1',
    ],
    platforms='any',
)
