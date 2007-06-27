#!/usr/bin/env python

'''Upload dist/ files to code.google.com.  For Alex only :-)
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import os
import sys

base = os.path.dirname(__file__)
root = os.path.join(base, '../..')
dist = os.path.join(root, 'dist')

sys.path.insert(0, root)
import pyglet

import googlecode_upload

if __name__ == '__main__':
    version = 'pyglet-%s' % pyglet.version
    print 'Preparing to upload %s' % version

    password = open(os.path.expanduser('~/.googlecode-passwd')).read().strip()

    descriptions = {}
    for line in open(os.path.join(base, 'descriptions.txt')):
        suffix, description = line.split(' ', 1)
        descriptions[suffix] = description.strip()

    files = {}
    for filename in os.listdir(dist):
        if filename.startswith(version):
            description = descriptions.get(filename[len(version):])
            if not description:
                print 'No description for %s' % filename
                sys.exit(1)
            description = '%s %s' % (pyglet.version, description)
            files[filename] = description
            print filename
            print '   %s' % description

    print 'Ok to upload? [type "y"]'
    if raw_input().strip() != 'y':
        print 'Aborted.'
        sys.exit(1)

    for filename, description in files.items():
        status, reason, url = googlecode_upload.upload(
            os.path.join(dist, filename),
            'pyglet',
            'Alex.Holkner',
            password,
            description,
            None)
        if url:
            print 'OK: %s' % url
        else:
            print 'Error: %s (%s)' % (reason, status)

    print 'Done!'
