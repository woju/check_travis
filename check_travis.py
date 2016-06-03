#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 et
#
# Copyright (c) 2016 Wojtek Porczyk <woju@invisiblethingslab.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

'''Icinga/Nagios plugin for checking Travis build status

https://github.com/woju/check_travis
'''

import argparse
import json
import posixpath
import pprint
import sys
import urllib.error
import urllib.request

__version__ = '1'
__author__ = 'Wojtek Porczyk <woju@invisiblethingslab.com>'

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3

# https://github.com/travis-ci/travis.rb/blob/master/lib/travis/client/states.rb
# especially "color"
RETCODES = {
    'passed':   STATUS_OK,
    'ready':    STATUS_OK,

    'created':  STATUS_WARNING,
    'queued':   STATUS_WARNING,
    'received': STATUS_WARNING,
    'started':  STATUS_WARNING,

    'failed':   STATUS_CRITICAL,
    'errored':  STATUS_CRITICAL,
    'cancelled':STATUS_CRITICAL,
}


parser = argparse.ArgumentParser(
    description='''\
{description}
Version {version}

Copyright (c) 2016  {author}
Distributed under MIT licence.'''.format(
        description=__doc__.split('\n')[0],
        version=__version__,
        author=__author__),
    epilog='''\
Homepage: https://github.com/woju/check_travis
Report bugs: https://github.com/woju/check_travis/issues/new-issue''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('--api', '-H',
    default='https://api.travis-ci.org/',
    help='API prefix (default: %(default)r)')

parser.add_argument('--warning', '-w', metavar='THRESHOLD',
    type=int,
    default=0,
    help='warning threshold for build time [s] (default: 0, don\'t check)')

parser.add_argument('--critical', '-c', metavar='THRESHOLD',
    type=int,
    default=0,
    help='critical threshold for build time [s] (default: 0, don\'t check)')

parser.add_argument('--debug', '-d',
    action='store_true', default=False,
    help=argparse.SUPPRESS)

parser.add_argument('repo', metavar='OWNER/REPO',
    help='repo slug')


def main(args=None):
    args = parser.parse_args()
    endpoint = posixpath.join(args.api, 'repos', args.repo)

    try:
        response = urllib.request.urlopen(urllib.request.Request(endpoint,
            headers={
                'Accept': 'application/vnd.travis-ci.2+json',
                'User-Agent':
                    'check_travis/{} ({})'.format(__version__, __author__)}))

    except urllib.error.HTTPError as e:
        print('{args.repo} check failed: {e!s}'.format(args=args, e=e))
        return STATUS_CRITICAL

    response = json.loads(response.read().decode('utf-8'))
    if args.debug:
        pprint.pprint(response, stream=sys.stderr)

    if not response['repo']['last_build_state']:
        print('{response[repo][slug]} has no builds'.format(response=response))
        return STATUS_UNKNOWN

    retcode = RETCODES.get(response['repo']['last_build_state'], STATUS_UNKNOWN)
    lenghty = False
    for status, threshold in (
            (STATUS_WARNING, args.warning),
            (STATUS_CRITICAL, args.critical)):
        if threshold and response['repo']['last_build_duration'] > threshold:
            retcode = max(retcode, status)
            lenghty = True

    print(
        '{response[repo][slug]}'
        ' {lenghty}build #{response[repo][last_build_number]}'
        ' {response[repo][last_build_state]}'
        ' at {response[repo][last_build_finished_at]}'
        ' ({response[repo][last_build_duration]} s)'
        '|last_build_duration={response[repo][last_build_duration]}s'
        ';{warning};{critical};0'.format(
            response=response,
            lenghty='lenghty ' if lenghty else '',
            warning=args.warning or '',
            critical=args.critical or ''))

    return retcode


if __name__ == '__main__':
    sys.exit(main())
