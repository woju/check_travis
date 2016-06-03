#!/usr/bin/env python3
# vim: fileencoding=utf-8

import email
import os

import setuptools

import check_travis

if __name__ == '__main__':
    author, author_email = email.utils.parseaddr(check_travis.__author__)
    setuptools.setup(
        name='check_travis',
        version=check_travis.__version__,
        url='https://github.com/woju/check_travis',
        author=author,
        author_email=author_email,

        description=check_travis.__doc__.split('\n', 1)[0],
        long_description=open(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'README.rst'),
            encoding='utf-8').read(),

        license='MIT',

        py_modules=['check_travis'],
#       entry_points={
#           'console_scripts': 'check_travis = check_travis:main',
#       },
        scripts=['check_travis'],
        data_files=[
            ('/usr/lib/nagios/plugins', ['check_travis']),
            ('/usr/share/doc/check_travis', ['README.rst', 'icinga2.conf']),
        ])
