#!/usr/bin/env python

# Miro - an RSS based video player application
# Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011
# Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
#
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

"""
This script is for importing a Launchpad export of .po files.  It
handles both the **full export** case and individual .po files.  It:

* extracts files form launchpad-export.tar.gz,
* moves files from democracyplayer/* directory to the current one,
* fixes the filenames to what Miro uses,
* fixes some bugs we've seen in some of the translations,
* calls msgfmt on the .po files creating .mo files, and
* cleans up afterwards

It's just a utility script.  If you find it needs additional bits,
let us know.
"""

import subprocess
import glob
import os.path
import os
import glob
import sys

def get_files():
    return [mem for mem in os.listdir(".") if mem.endswith(".po")]

def fix_names():
    files = get_files()
    for pofile in files:
        newfilename = pofile
        for repl in ["democracyplayer_", "democracyplayer-"]:
            newfilename = newfilename.replace(repl, "")
        if newfilename != pofile:
             os.system("mv %s %s" % (pofile, newfilename))

def fix_ro_plurals():
    bad_files = 0
    bad_str = '"Plural-Forms: nplurals=3; plural=((n == 1 ? 0: (((n %\\n"\n"100 > 19) || ((n % 100 == 0) && (n != 0))) ? 2: 1)));\\n"'

    good_str = '"Plural-Forms: nplurals=3; plural=((n == 1 ? 0: (((n % 100 > 19) || ((n % 100 == 0) && (n != 0))) ? 2: 1)));\\n"'
    ro_path = os.path.normpath(os.path.join(__file__, '..', 'ro.po'))
    f = open(ro_path)
    content = f.read()
    f.close()
    if bad_str in content:
        print 'fixing ro.po'
        bad_files += 1
        f = open(ro_path, 'wt')
        f.write(content.replace(bad_str, good_str))
        f.close()
    print "(bad files: %d)" % bad_files

def fix_pound_pipe():
    bad_files = 0
    files = get_files()
    for pofile in files:
        f = open(pofile, "r")
        content = f.readlines()
        lines = [line for line in content if not line.startswith("#|")]
        f.close()
        if len(content) != len(lines):
            bad_files += 1
            f = open(pofile, "w")
            f.write("".join(lines))
            f.close()
    print "(bad files: %d)" % bad_files

def build_catalogs():
    files = get_files()
    for pofile in files:
        mofile = "%s.mo" % pofile[:-3]
        os.system("msgfmt %s -o %s" % (pofile, mofile))

def main(args):
    if not os.path.exists("./launchpad-export.tar.gz"):
        print "launchpad-export.tar.gz file not found."
        print "Aborting."
        return

    print "Extracting files...."
    subprocess.call(["tar", "-xzvf", "launchpad-export.tar.gz"])
    args = glob.glob("./democracyplayer/*")
    if args:
        args.insert(0, "mv")
        args.append(".")
        print "Moving files from democracyplayer/ to here...."
        subprocess.call(args)
        print "Removing empty democracyplayer directory...."
        subprocess.call(["rm", "-rf", "democracyplayer"])
    print "FIXING NAMES...."
    fix_names()
    print "FIXING #| issues...."
    fix_pound_pipe()
    print "FIXING RO PLURALS...."
    fix_ro_plurals()
    print "BUILDING .mo FILES...."
    build_catalogs()

    print "Removing cruft...."
    subprocess.call(["rm", "-rf", "democracyplayer", "launchpad-export.tar.gz", "democracyplayer.pot"])

if __name__ == "__main__":
    main(sys.argv[1:])
