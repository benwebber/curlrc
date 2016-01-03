# -*- coding: utf-8 -*-

import setuptools

setuptools.setup(
    name='curlrc',
    version='0.1.0',
    url='https://github.com/benwebber/curlrc/',

    description="Treat curl configuration files as curlrc subcommands.",
    long_description=open('README.rst').read(),

    author='Ben Webber',
    author_email='benjamin.webber@gmail.com',

    py_modules=['curlrc'],

    zip_safe=False,

    entry_points={
        'console_scripts': [
            'curlrc = curlrc:main',
        ],
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
