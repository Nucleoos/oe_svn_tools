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
    logger.info("Repository's youngget revision is <%s>" % last_rev)
    
    try:
        #######################################################################
        # Step 1. dump repository generate new baseline bakcup

        repo_dump_path = os.path.join(repo_backup_basedir, repo_name)
        if not os.path.exists(repo_dump_path):
            os.makedirs(repo_dump_path)

        # check if full dump file has existed, skip backup process
        repo_dump_file = os.path.join(repo_dump_path, repo_name + "-baseline-" + last_rev)
        if os.path.exists(repo_dump_file):
            logger.info("Dump file %s already exists!" % (repo_dump_file))
            logger.info("Backup completed !")
            return 0
        
        repo_dump_file += ".tmp"
        #repo_dump_file = os.path.join(repo_dump_path, repo_name + "-baseline-" + last_rev + ".tmp")
        repo_dump_file_obj = open(repo_dump_file, "wb")
        logger.info("Dumping to temp file: %s" % repo_dump_file)
        
        cmd = "%s dump -q %s" % (svn_admin, repo_path)
        ret = subprocess.call(cmd, stdout=repo_dump_file_obj) # redirect output to a file
        if ret <> 0:
            return 1
        repo_dump_file_obj.close()
        
        #######################################################################
        # Step 2. generate new baseline file 

        repo_baseline_file = repo_dump_file[:-4] # cut '.tmp' from tail

        if os.path.exists(repo_baseline_file):
            os.remove(repo_baseline_file)
            
        shutil.move(repo_dump_file, repo_baseline_file) 
        logger.info("Creating baseline file: %s" % repo_baseline_file)
        
        #######################################################################
        # Step 3. delete incremental backup files 

        outlist = os.listdir(repo_dump_path)
        for item in outlist:
            full_path=os.path.join(repo_dump_path, item)
            if item.startswith('commit-'):
                logger.info("Remove previous incremental backup file: %s" % \
                            full_path)
                os.remove(full_path)

    except Exception as e:
        logger.info("Backup failed, catched exception: \n\t" + str(e))
        return 1

    logger.info("Backup completed !")
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

if __name__ == "__main__":

    logger = logging.getLogger('svn_backup')
    logger.setLevel(logging.INFO)
    
    fh = logging.FileHandler("svn_backup.log")
    fh.setLevel(logging.INFO)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)-15s - %(levelname)-10s - %(message)s')     
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    parser = argparse.ArgumentParser()
    #group = parser.add_mutually_exclusive_group(required=True)
    
    #group.add_argument("--repos_dir", help="repos folder")
    #group.add_argument("--prj_dir", help="project folder")
    parser.add_argument("--repos_dir", help="repos folder", required=True)
    parser.add_argument("--project", help="project name")
    parser.add_argument("--bak_dir", help="backup base folder", required=True)
    args = parser.parse_args()
    #print args
    
    if len(args.bak_dir) > 0 and os.path.exists(args.bak_dir):
        repo_backup_basedir = args.bak_dir
        
    if args.repos_dir and \
        len(args.repos_dir) > 0 and \
        os.path.exists(args.repos_dir): 
        repo_basedir = args.repos_dir

    '''        
    if args.prj_dir and \
        len(args.prj_dir) > 0 and \
        os.path.exists(args.prj_dir):
        print 'Backup repository:%s ...' % args.prj_dir
        logger.info('Backup repository:%s ...' % args.prj_dir)
        #sys.exit(svn_fullbackup(args.prj_dir)
    '''
    
    if args.project:
        repo_path=os.path.join(repo_basedir, args.project)
        if os.path.isdir(repo_path):
            logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            logger.info('Backup repository: %s ...' % repo_path)
            sys.exit(svn_fullbackup(repo_path))
    else:
        logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        logger.info('Backup all projects in repositories: %s' % repo_basedir)
        sys.exit(main(repo_basedir))
        
    
    #print repo_backup_basedir
    #print repo_basedir
    
        