#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import datetime 
import shutil



####################################################
# Global defines
repo_basedir='e:\Repositories'
repo_backup_basedir='e:\svn_backup_test'
svn_admin='svnadmin.exe'
svn_look='svnlook.exe'

class MyError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)
        
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

def svn_create(repo_path):
    '''
    svnadmin create ¡ª Create a new, empty repository.
    '''

    cmd = "%s create %s" % (svn_admin, repo_path)
    return subprocess.call(cmd)

def svn_load(repo_path, repo_dump_file):
    '''
    restore repository from a dump file
    '''
    
    repo_dump_file_obj = open(repo_dump_file, "rb")
    
    cmd = "%s load -q %s" % (svn_admin, repo_path)
    ret = subprocess.call(cmd, stdin=repo_dump_file_obj) # redirect input from a file
    repo_dump_file_obj.close()

    return ret
    
def svn_repo_restore(repo_dump_path):
    ''' 
    restore repository from dump file
    repo_dump_path is a folder that store repo's dump file 
    '''

    repo_name = os.path.basename(repo_dump_path) 
    print "Restore repository <%s>" % (repo_name)
    
    try:
        ###########################################################################
        # Step 1. if repo is not exist, create it !

        repo_path = os.path.join(repo_basedir, repo_name)
        if not os.path.exists(repo_path):
            print "Create respository <%s>" % (repo_path)
            ret = svn_create(repo_path)
            if ret <> 0:
                raise MyError("Create repo failed !")
        else:
            '''
            TODO: Get head version
            '''

        
        ###########################################################################
        # Step 2. restore repository from newest dump file 

        repo_backup_file_list=[] 

        '''
        outlist = os.listdir(repo_dump_path)    
        for item in outlist:
            full_path = os.path.join(repo_dump_path, item)
            if not os.path.isdir(full_path):
                repo_backup_file_list.append(full_path)
                print "dump file is <%s>" % (full_path)
        return 0
        '''
        last_rev = '7'
        ''' 
        TODO: If head version >= last_rev no need restore
        '''
        repo_dump_file = os.path.join(repo_dump_path, repo_name + "-baseline-" + last_rev)
        print "Restore from dump file <%s>" % (repo_dump_file)
        
        ret = svn_load(repo_path, repo_dump_file)
        if ret <> 0:
            raise MyError("restore repo failed !")
        
    except Exception as e:
        print "Restore failed, catched exception: \n\t" + str(e) 
            
        return 1

    print "Restore completed !"
    return 0


def main(repo_parentpath, *args, **kwargs):
    '''
    The special syntax, *args and **kwargs in function definitions is used to pass a variable number of arguments to a function. 
    The single asterisk form (*args) is used to pass a non-keyworded, variable-length argument list, 
    and the double asterisk form is used to pass a keyworded, variable-length argument list.
    '''

    print "Restore subversion repositories..."

    repo_backup_path_list=[] 

    outlist = os.listdir(repo_parentpath)    
    for item in outlist:
        full_path=os.path.join(repo_parentpath, item)
        if os.path.isdir(full_path):
            repo_backup_path_list.append(full_path)

    for repo_backup_path in repo_backup_path_list:
        if svn_repo_restore(repo_backup_path) <> 0:
            return 1

    return 0
    
####################################################
# Main body

if len(sys.argv) > 1:
    repo_backup_basedir = sys.argv[1]

sys.exit(main(repo_backup_basedir))
