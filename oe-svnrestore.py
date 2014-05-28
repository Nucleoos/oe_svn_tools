#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import datetime 
import shutil
import argparse # new in version 2.7
import logging



####################################################
# Global defines
repo_basedir='e:\Repositories'
repo_backup_basedir='e:\svn_backup'
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
    logger.info("Restore repository <%s>" % (repo_name))
    
    try:
        #######################################################################
        # Step 1. if repo is not exist, create it !

        repo_path = os.path.join(repo_basedir, repo_name)
        if not os.path.exists(repo_path):
            logger.info("Create respository <%s>" % (repo_path))
            ret = svn_create(repo_path)
            if ret <> 0:
                raise MyError("Create repo failed !")
        
        #######################################################################
        # Step 2. generate dump file list 

        repo_backup_file_list=[] 

        outlist = os.listdir(repo_dump_path)    
        for item in outlist:
            full_path = os.path.join(repo_dump_path, item)
            if not os.path.isdir(full_path):
                repo_backup_file_list.append(full_path)
                #print "dump file is <%s>" % (full_path)
        
        #######################################################################
        # Step 3. restore repository from dump file 

        for repo_dump_file in repo_backup_file_list:
            logger.info("Restore from dump file <%s>" % (repo_dump_file))
            ret = svn_load(repo_path, repo_dump_file)
            if ret <> 0:
                raise MyError("restore repo failed !")
        
        '''
        last_rev = '7'        
        repo_dump_file = os.path.join(repo_dump_path, repo_name + "-baseline-" + last_rev)
        print "Restore from dump file <%s>" % (repo_dump_file)
        
        ret = svn_load(repo_path, repo_dump_file)
        if ret <> 0:
            raise MyError("restore repo failed !")
        '''
        
    except Exception as e:
        logger.info("Restore failed, catched exception: \n\t" + str(e))
            
        return 1

    logger.info("Restore completed !")
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
'''
if len(sys.argv) > 1:
    repo_backup_basedir = sys.argv[1]
    
sys.exit(main(repo_backup_basedir))
'''

if __name__ == "__main__":

    logger = logging.getLogger('svn_restore')
    logger.setLevel(logging.INFO)
    
    fh = logging.FileHandler("svn_restore.log")
    fh.setLevel(logging.INFO)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)-15s - %(levelname)-10s - %(message)s')     
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
        
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos_dir", help="repos folder", required=True)
    parser.add_argument("--project", help="project name")
    parser.add_argument("--bak_dir", help="backup base folder", required=True)
    args = parser.parse_args()

    
    if len(args.bak_dir) > 0 and os.path.exists(args.bak_dir):
        repo_backup_basedir = args.bak_dir
        
    if args.repos_dir and \
        len(args.repos_dir) > 0 and \
        os.path.exists(args.repos_dir): 
        repo_basedir = args.repos_dir

    if args.project:
        repo_backup_path=os.path.join(repo_backup_basedir, args.project)
        if os.path.isdir(repo_backup_path):
            logger.info('Restore repository <%s> from <%s>' % \
                (args.project, repo_backup_path))
            sys.exit(svn_repo_restore(repo_backup_path))
    else:
        logger.info('Restore all projects in backup folder: %s' % \
            repo_backup_basedir)
        sys.exit(main(repo_backup_basedir))

    sys.exit(0)
