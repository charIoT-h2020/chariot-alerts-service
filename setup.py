#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'falcon',
    'influxdb',
    'chariot_base',
    'paho-mqtt',
    'asyncio',
    'gmqtt',
    'influxdb',
    'cloudant',
    'ibmiotf',
    'pytest',
    'fastecdsa',
    'ecdsa',
    'pycrypto',
    'jaeger-client',
    'pytest-asyncio'
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="George Theofilis",
    author_email='g.theofilis@clmsuk.com',
    classifiers=[
        'License :: OSI Approved :: Eclipse Public License 1.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    description="CharIoT Alert Service",
    install_requires=requirements,
    license="EPL-1.0",
    long_description=readme,
    include_package_data=True,
    keywords='chariot_alert_service',
    name='chariot_alert_service',
    packages=find_packages(include=[
        'chariot_alert_service',
        'chariot_alert_service.*'
    ]),
    entry_points={
        'console_scripts': [
            'alerts = chariot_alert_service.digester.alerts:main'
        ]
    },
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.com/chariot-h2020/chariot-alerts-service',
    version='0.11.0',
    zip_safe=False,
)
