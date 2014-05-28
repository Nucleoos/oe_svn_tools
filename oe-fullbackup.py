#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import datetime 
import shutil



####################################################
# Global defines
repo_basedir='d:\Repositories'
repo_backup_basedir='e:\svn_backup'
svn_admin='svnadmin.exe'
svn_look='svnlook.exe'


def svn_verify(repo_path):
    '''
    verify subversion repository if normal 
    Run this command if you wish to verify the integrity of your repository. 
    This basically iterates through all revisions in the repository by 
    internally dumping all revisions and discarding the output.
    '''

    cmd = "%s verify %s" % (svn_admin, repo_path)
    return subprocess.call(cmd)

def svn_getyoungest_revision(repo_path):

    cmd = "%s youngest %s" % (svn_look, repo_path)
    subproc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, errout = subproc.communicate()
    if subproc.returncode == 0:
        return out.strip()
    else:
        return ""

def svn_fullbackup(repo_path):
    ''' full dump repository '''

    repo_name = os.path.basename(repo_path) 
    today_str = datetime.date.today().strftime("%Y%m") # no use 
    last_rev  = svn_getyoungest_revision(repo_path)
    if len(last_rev) <= 0:
        return 1
    print "Repository's youngget revision is <%s>" % last_rev
    
    try:
        ###########################################################################
        # Step 1. dump repository generate new baseline bakcup

        repo_dump_path = os.path.join(repo_backup_basedir, repo_name)
        if not os.path.exists(repo_dump_path):
            os.makedirs(repo_dump_path)

        repo_dump_file = os.path.join(repo_dump_path, "baseline-" + last_rev + ".tmp")
        repo_dump_file_obj = open(repo_dump_file, "wb")
        print "Dumping to temp file: %s" % repo_dump_file
        
        cmd = "%s dump -q %s" % (svn_admin, repo_path)
        ret = subprocess.call(cmd, stdout=repo_dump_file_obj) # redirect output to a file
        if ret <> 0:
            return 1
        repo_dump_file_obj.close()
        
        ###########################################################################
        # Step 2. generate new baseline file 

        repo_baseline_file = repo_dump_file[:-4] # cut '.tmp' from tail

        if os.path.exists(repo_baseline_file):
            os.remove(repo_baseline_file)
            
        shutil.move(repo_dump_file, repo_baseline_file) 
        print "Creating baseline file: %s" % repo_baseline_file
        
        ###########################################################################
        # Step 3. delete incremental backup files 

        outlist = os.listdir(repo_dump_path)
        for item in outlist:
            full_path=os.path.join(repo_dump_path, item)
            if item.startswith('commit-'):
                print "Remove previous incremental backup file: %s" % full_path
                os.remove(full_path)

    except Exception as e:
        print "Backup failed, catched exception: \n\t" + str(e) 
        return 1

    print "Backup completed !"
    return 0


def main(repo_parentpath, *args, **kwargs):
    '''
    The special syntax, *args and **kwargs in function definitions is used to pass a variable number of arguments to a function. 
    The single asterisk form (*args) is used to pass a non-keyworded, variable-length argument list, 
    and the double asterisk form is used to pass a keyworded, variable-length argument list.
    '''

    print "Backup subversion repositories..."

    repo_path_list=[] 

    outlist = os.listdir(repo_parentpath)    
    for item in outlist:
        full_path=os.path.join(repo_parentpath, item)
        if os.path.isdir(full_path):
            repo_path_list.append(full_path)

    for repo_path in repo_path_list:
        print 'Backup repository:%s ...' % repo_path
        if svn_fullbackup(repo_path) <> 0:
            return 1

    return 0
    
####################################################
# Main body

if len(sys.argv) > 1:
    repo_basedir = sys.argv[1]

sys.exit(main(repo_basedir))


