

"""
This script helps you find files on a remote FTP server.
It's also possible to search the cached version of the
site with no network access.
"""

import re
import sys
import anydbm
import argparse
from ftplib import FTP
from os import path
import os

__version__ = "0.1"
__author__ = "Hao Wang"


class FtpFileFinder(object):
    db = None
    ftp = None
    dirs = []
    dirname = ''

    def __init__(self):
        super(FtpFileFinder, self).__init__()

    def openRemote(self, server, username=None, password=None):
	if not path.exists(server + '.arch'):
        	self.db = anydbm.open(server + '.arch', 'n')
        self.ftp = FTP(server)
        self.ftp.login(username, password)

    def closeRemote(self):
        self.ftp.quit()
        self.ftp = None
        self.db.sync()

    def findFile(self, filename):
	filelist=[]
        for k,v in self.db.items():
	    
            if k.lower().find(filename) != -1:
                filelist.append(k)
	return filelist

    def loadFromFile(self, archfile):
        self.db = anydbm.open(archfile, 'r')

    def listDir(self, dirname=''):
        if len(dirname) > 0 and len(self.dirname) == 0:
            self.dirname = dirname
        self.ftp.cwd(self.dirname)
        self.ftp.retrlines('LIST', self.addFile)
	self.ftp.cwd("/")

        while len(self.dirs) > 1:
            self.dirname = self.dirs.pop()
	    print self.dirname
	    self.ftp.cwd(self.dirname)
	    self.ftp.retrlines('LIST', self.addFile)
            self.ftp.cwd("/")

    def addFile(self, line):
        arr = line.split(' ')
        fname = arr[len(arr)-1]
        absolute = self.dirname + '/' + fname

        m = re.match('^d.*', line)
        if m!= None:
            if fname!='.' and fname!='..':
                self.dirs.append(absolute)
        elif fname!='.' and fname!='..':
            self.db[absolute] = fname
   
	#first time running store all the file to the arch db, 
	#later run, first loadfile

    def downloadByName(self,name):
	"""give the name of bacteria strain, download the gbk file,with the of strain name+filename,take example, prochlorococcus strain, download files with the name pro..._CP00878.gbk"""
	 #set the path to root
	filelist=self.findFile(name)
	newfilelist=self.filterGbk(filelist)
	if not path.exists(name):
		os.mkdir(name)
	os.chdir(name)
	for eachfile in newfilelist:
		dirname=eachfile[0]
		filename=eachfile[1]
		newname=eachfile[2]
		print dirname,filename,newname
		self.ftp.cwd("/")
		self.ftp.cwd(dirname)

		gbkfile=open(newname,"wb")
		
		print 'Getting ' + newname
		self.ftp.retrbinary('RETR ' + filename, gbkfile.write)
		print 'Closing file ' + newname
		gbkfile.close()
	
    def filterGbk(self,filelist):
	newfilelist=[]
	for file in filelist:
		
		if file.find("gbk")>0:
			dirname=path.dirname(file)
			filename=path.basename(file)
			newname=file.split("/")[-2]+"_"+filename
			newfilelist.append([dirname,filename,newname])
	return newfilelist


def main():	
	fff=FtpFileFinder()
	fff.openRemote("ftp.ncbi.nih.gov")
	#fff.listDir('genbank/genomes/Bacteria')
	#fff.closeRemote()
	fff.loadFromFile('ftp.ncbi.nih.gov.arch')
	fff.downloadByName("synechococcus")

if __name__ == '__main__':
    main()

 

