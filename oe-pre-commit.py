#!/usr/bin/env python

'''
Subversion pre-commit hook which currently checks that the commit contains
a commit message to avoid commiting empty changesets which tortoisesvn seems
to have a habbit of committing.

Work with VisualSVN Server 
zouxy <zxyu@os-easy.com>

svnlook log REPOS_PATH 'Print the log message, followed by a newline character.'
    options:
        --revision (-r) REV
        --transaction (-t) TXN

    details see http://www.visualsvn.com/support/svnbook/ref/svnlook/c/changed/

svnlook changed REPOS_PATH 'Print the paths that were changed.'
    options:
        --copy-info
        --revision (-r) REV
        --transaction (-t) TXN

    details see http://www.visualsvn.com/support/svnbook/ref/svnlook/c/changed/

'''

import sys, os, string
from subprocess import *

svn_look ='C:\\Program Files\\VisualSVN Server\\bin\\svnlook.exe'

def filter_filetype(repo_path, txn):

    lines = ""
    illegal_filetypes = ['.obj', '.usr', '.tmp', '.suo', '.ncb', 'pdb', 'swp', '.db']
    
    cmd = '\"%s\" changed -t \"%s\" \"%s\" ' % (svn_look, txn, repo_path)
    subproc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, errout = subproc.communicate()
    if subproc.returncode == 0:
        lines = out.split('\n')
    else:
        sys.stderr.write("%s return error:%s\n" % (cmd, errout))
        sys.exit(1)

    for line in lines:
        if len(line.rstrip('\r').rstrip('\n').strip()) <= 0: continue

        mode = line.split()[0]
        #sys.stderr.write("mode=%s\n" % mode) # debug code
        if mode.find('A') == -1: continue

        filename = line.split()[1]
        for filetype in illegal_filetypes:
            if filename.endswith(filetype):
                sys.stderr.write("Please do not add the following filetypes: \n")
                sys.stderr.write("%s\n" % str(illegal_filetypes))
                sys.exit(1)
                
    return 0


def filter_logmessage(repo_path, txn):

    lines = ""
    
    #sys.stderr.write("repos_path=%s\n" % repo_path) # debug code
    cmd = '\"%s\" log -t \"%s\" \"%s\"' % (svn_look, txn, repo_path)
    subproc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, errout = subproc.communicate()
    if subproc.returncode == 0:
        lines = out.split('\n')
        sys.stderr.write("svnlook return :%s\n" % (out))
    else:
        sys.stderr.write("svnlook return error:(%d)%s\n" % (subproc.returncode, errout))
        sys.exit(1)
    
    chars = 0
    for line in lines:
        #sys.stderr.write("commit log:<%s>\n" % line.rstrip('\r').rstrip('\n')) # debug code
        chars = chars + len(line.rstrip('\r').rstrip('\n').strip()) 

    if chars < 10:
        sys.stderr.write("Please enter a commit message which details what has changed during this commit.\n")
        sys.exit(1)

    #sys.stderr.write("commit log chars=%d\n" % chars) # debug code
    return 0


def main(repo_path, txn):

    filter_logmessage(repo_path, txn)
    
    filter_filetype(repo_path, txn)

   
if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: %s REPOS TXN\n" % (sys.argv[0]))
    else:
        sys.exit(main(sys.argv[1], sys.argv[2]))

