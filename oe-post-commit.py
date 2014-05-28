#!/usr/bin/env python

"""
Subversion post-commit hook which dump commited revision 

Work with VisualSVN Server 
zouxy <zxyu@os-easy.com>
"""

import sys, os
import subprocess


####################################################
# Global defines
repo_backup_basedir='E:\svn_backup'
svn_admin='C:\\Program Files\\VisualSVN Server\\bin\\svnadmin.exe'


def filter_incrbackup(repo_path, revision):

    try:
        repo_name = os.path.basename(repo_path) 
        repo_dump_path = os.path.join(repo_backup_basedir, repo_name)
        if not os.path.exists(repo_dump_path):
            os.makedirs(repo_dump_path)

        repo_dump_file = os.path.join(repo_dump_path, "commit-" + revision)
        repo_dump_file_obj = open(repo_dump_file, "wb")

        cmd = '\"%s\" dump \"%s\" --revision \"%s\" --incremental' % (svn_admin, repo_path, revision)
        ret = subprocess.call(cmd, stdout=repo_dump_file_obj) # redirect output to a file
        if ret <> 0:
            sys.stderr.write("Backup failed, return code: %d\n" % ret)
            sys.exit(1)
            
        repo_dump_file_obj.close()
        
    except Exception as e:
        sys.stderr.write("Backup failed, catched exception: %s\n" % str(e))
        sys.exit(1)
        
    return 0


def main(repo_path, revision):

    filter_incrbackup(repo_path, revision)
    
    sys.exit(0)


   
if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: %s REPO_PATH REV\n" % (sys.argv[0]))
    else:
        main(sys.argv[1], sys.argv[2])

