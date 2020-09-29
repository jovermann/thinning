#!/usr/bin/python3
#
# thinning.py - remove obsolete backup dirs
#
# Requires Python >= 3.4 (re.fullmatch())
#
# Copyright (C) 2020 by Johannes Overmann <Johannes.Overmann@joov.de>

import argparse
import os
import sys
import shutil
import re
import datetime

# Command line options.
options = None

statNumRemoved = 0
statNumKept = 0
statNumTotal = 0


class Dir:
    """Backup directory meta info.
    """
    
    def __init__(self, basedir, dir):
        """Constructor.
        """
        self.dir = dir  # 2020-12-31
        self.basedir = basedir # /backup/backup_foo
        self.path = os.path.join(basedir, dir)
        self.keep = False
        self.ord = 0
        self.keepReason = ""
        if self.isDateName():
            self.ord = datetime.datetime.strptime(self.dir, "%Y-%m-%d").toordinal()

    def isDateName(self):
        """Return true iff this dir has the format YYYY-MM-DD.
        """
        return re.fullmatch("20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]", self.dir) != None
    
    def __repr__(self):
        """String representation.
        """
        return "{} {} {} {}".format(self.path, self.ord, ["", "keep"][self.keep], self.keepReason)


def tagEvery(dirs, n, keepReason, starting = 0):
    """Tag every n days in 'dirs' at least.
    """
    start = dirs[0].ord
    end = dirs[-1].ord
    last = start
    prevd = dirs[0]
    for d in dirs:
        if d.keep:
            last = d.ord
        else:
            if d.ord - last == n:
                if d.ord >= starting:
                    d.keep = True
                    d.keepReason += keepReason
                last = d.ord
            elif d.ord - last > n:
                if prevd.ord >= starting:
                    prevd.keep = True
                    prevd.keepReason += keepReason
                last = prevd.ord                
                if d.ord - last >= n:
                    if d.ord >= starting:
                        d.keep = True
                        d.keepReason += keepReason                    
                    last = d.ord
            else:                
                pass                
        prevd = d

    
def thinDir(basedir):
    """Remove obsolete backups under basedir.
    """
    global statNumRemoved
    global statNumKept
    global statNumTotal
    if options.verbose:
        print("Processing dir {}".format(basedir))
    dirs = sorted(os.listdir(basedir))
    
    # Create list of Dirs.
    dirs = [Dir(basedir, d) for d in dirs]
    
    # Extract only non-link dirs.
    dirs = [d for d in dirs if os.path.isdir(d.path) and not os.path.islink(d.path)]
    
    # Extract only sane dirnames.
    dirs = [d for d in dirs if d.isDateName()]
    
    if len(dirs) == 0:
        print("Directory {} does not contain any backup dirs.".format(basedir))
        return
    
    # Tag oldest.
    dirs[0].keep = True
    dirs[0].keepReason += "o";
    
    # Tag one every 28 days at least.
    tagEvery(dirs, 28, "m")
        
    # Tag one every week at least.
    tagEvery(dirs, 7, "w", starting = dirs[-1].ord - options.keep_weekly)
    
    # Tag last 30 backups.
    for d in dirs[-options.keep_latest:]:
        d.keep = True
        d.keepReason += "d";
    
    if options.verbose >= 3:
        for d in dirs:
            print(d)
            
    # Remove obsolete dirs.
    for d in dirs:
        statNumTotal += 1
        if d.keep:
            if options.verbose >= 2:
                print("keeping  {} ({})".format(d.path, d.keepReason))
            statNumKept += 1
            continue
        if options.verbose:
            print("removing {}".format(d.path))
        if not options.dummy:
            shutil.rmtree(d.path)
        statNumRemoved += 1
            
            



def main():
    """Main function of this module.
    """
    global options
    usage = """%(prog)s [OPTIONS] DIRS...
    
Remove obsolete backup dirs from a set of daily incremental backups.
    
This tool finds all subdirectories under the given DIR(S) which match the
pattern YYYY-MM-DD (ISO 8601 date) and removes all obsolete subdirs.
All subdirs matching the pattern are deleted, except:
- (d) Daily: The latest 30 backups are never deleted 
             (can be configured with --keep-latest).
- (w) Weekly: The weekly backups in the latest 90 days since the latest backup
              are never deleted (can be configured with --keep-weekly).
- (m) Monthly: At least one backup every 28 days is kept.
- (o) Oldest: The oldest backup is never deleted.

- The current date and the filesystem date are not taken into account. 
  Just the filenames are inspected.
- Subdirs not matching the YYYY-MM-DD pattern are ignored and are not deleted.

(The characters in parentheses indicate the reason to keep a subdirectory when
verbosity level 2 (-VV) is specified.)
    
Examples:

Given the following backup dir layout:
/backup/main/2020-01-20
/backup/main/2020-01-21
/backup/main/2020-02-22
...
        
Check what would be deleted, without actually deleting it:
> thinning.py -0V /backup/main
    
Delete obsolete backup dirs:
> thinning.py -V /backup/main
"""
    version = "0.1.3"
    parser = argparse.ArgumentParser(usage = usage + "\n(Version " + version + ")\n")
    parser.add_argument("args", nargs="*", help="Dirs to process.")
    parser.add_argument("-0", "--dummy", help="Dummy mode. Do not remove anything. Nothing changes on disk.", action="store_true", default=False)
    parser.add_argument("-V", "--verbose", help="Be more verbose. May be specified multiple times.", action="count", default=0) # -v is taken by --version, argh!
    parser.add_argument("-K", "--keep-latest", help="Always keep the latest N backups, regardless of their date (default 30).", type=int, default=30, metavar="N")
    parser.add_argument("-W", "--keep-weekly", help="Keep weekly backups for last N days relative to latest backup (default 90).", type=int, default=90, metavar="N")
    options = parser.parse_args()

    if len(options.args) == 0:
        parser.error("Please specify at least one directory.")
    
    try:
        # Fail early.
        for dir in options.args:
            os.listdir(dir)
        
        # Thin dir.
        for dir in options.args:
            thinDir(dir)

    except RuntimeError as e:
        print("Error: {}".format(str(e)))
    except OSError as e:
        print("Error: {}".format(str(e)))

    if options.verbose:
        print("--")
        print("{} dirs removed, {} dirs kept, {} dirs total".format(statNumRemoved, statNumKept, statNumTotal))


# Call main().
if __name__ == "__main__":
    main()

