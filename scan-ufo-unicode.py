#!/bin/env python3

import argparse
import glob
import operator
import os.path
import re
import sys
import xmltodict


def scan_unicode(dir):
    unicode = {}
    glyph_src = {}
    with open('{0}/glyphs/contents.plist'.format(dir), 'r') as f:
        doc = xmltodict.parse(f.read())
        glyphs = dict(zip(doc['plist']['dict']['key'], doc['plist']['dict']['string']))
        files = dict(zip(doc['plist']['dict']['string'], doc['plist']['dict']['key']))
    for path in glob.glob('{0}/glyphs/*.glif'.format(dir)):
        file = os.path.basename(path)
        if file in files:
            del files[file]
        else:
            print("File {0} not found in contents.plist for {1}".format(file, dir))
    if len(files) > 0:
        print("contents.plist for {0} refers to nonexistent files: {1}".format(dir, files))
    for glyph in glyphs.keys():
        file = glyphs[glyph]
        with open('{0}/glyphs/{1}'.format(dir, file), 'r') as f:
            doc = xmltodict.parse(f.read())
            name = doc['glyph']['@name']
            glyph_src[name] = doc
            if 'unicode' in doc['glyph']:
                unicode[glyph] = doc['glyph']['unicode']['@hex']
    return (unicode, glyph_src)


def save_unicode_list(outfile, file):
    (list, _) = scan_unicode(file)
    sorted_unicode = sorted(list.items(), key=operator.itemgetter(1))
    unicode = dict((v, k) for k, v in sorted_unicode)
    with open(outfile, 'w') as f:
        for code in unicode:
            print("{0} {1}".format(code, unicode[code]), file=f)


def build_nam_list(nam_file, nam_list = {}):
    with open(nam_file, 'r') as f:
        for line in f.readlines():
            m = re.match(r'0x(\S+)\s*(.*)', line)
            if m:
                nam_list[m.group(1)] = m.group(2)
    return nam_list


def compare_nam(nam, file):
    nam_list = build_nam_list(nam)
    (list, _) = scan_unicode(file)
    sorted_unicode = sorted(list.items(), key=operator.itemgetter(1))
    unicode = dict((v, k) for k, v in sorted_unicode)
    extra = unicode.copy()
    missing = {}
    for code in unicode.keys():
        if code in nam_list:
            del extra[code]
    for code in nam_list.keys():
        if code not in unicode:
            missing[code] = nam_list[code]
    if len(missing) > 0:
        print("Missing in {0}:".format(file))
        for code in missing:
            print("%s %s" % (code, missing[code]))
    if len(extra) > 0:
        print("Extra in {0}:".format(file))
        for code in extra:
            print("%s %s" % (code, extra[code]))
    if len(missing) == 0 and len(extra) == 0:
        print("All unicode entries in {0} are accounted for!".format(nam))


def main():
    parser = argparse.ArgumentParser(description='Scan UFO for unicode characters')
    parser.add_argument('file', nargs=1)
    parser.add_argument('--unicode-list', required=False, help='Save unicode list to file')
    parser.add_argument('--compare-nam', required=False, help='Compare unicode list to nam file')
    args = parser.parse_args()
    if args.unicode_list:
        save_unicode_list(args.unicode_list, args.file[0])
    elif args.compare_nam:
        compare_nam(args.compare_nam, args.file[0])
    else:
        print("Specify a processing option")


main()
# vim: ai ts=4 sts=4 et sw=4 ft=python
