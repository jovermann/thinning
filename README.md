# thinning.py
Remove obsolete backup dirs from a set of daily incremental backups.

## Usage
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
    
## Examples

Given the following backup dir layout:
```
/backup/main/2020-01-20
/backup/main/2020-01-21
/backup/main/2020-02-22
...
```
        
Check what would be deleted, without actually deleting it:
`> thinning.py -0V /backup/main`
    
Delete obsolete backup dirs:
`> thinning.py -V /backup/main`


## Options (help message)

```
usage: thinning.py [OPTIONS] DIRS...
    
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

(Version 0.1.3)

positional arguments:
  args                  Dirs to process.

optional arguments:
  -h, --help            show this help message and exit
  -0, --dummy           Dummy mode. Do not remove anything. Nothing changes on
                        disk.
  -V, --verbose         Be more verbose. May be specified multiple times.
  -K N, --keep-latest N
                        Always keep the latest N backups, regardless of their
                        date (default 30).
  -W N, --keep-weekly N
                        Keep weekly backups for last N days relative to latest
                        backup (default 90).
```                        
