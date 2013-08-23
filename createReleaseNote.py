#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from xml.dom.minidom import parseString
import sys
import getopt
import datetime
import glob
import shutil
import os
import subprocess

class dirPath(object):
    latexWorkingDir='latexWorkingDir/'
    exportedXMLDir='exportedXmls/'

    def checkDirectory(self,path):
        if not os.path.exists(path):
            os.makedirs(path)

    def cleanDirectoy(self,path):
        files = glob.glob(path + '*.*')
        for eachFile in files:
            shutil.os.remove(eachFile)

class TexFileBuilder(object):
    def headerOfFile(self,version, date):
        result ='\\newpage \n'
        result += '\\section*{'
        result += ' Version : ' + version
        result += ' released the ' + datetime.datetime.strptime(date, "%Y%m%d").strftime("%B %d, %Y")
        result += '}\n'
        result += '\\addcontentsline{toc}{section}{Version :' + version +'}\n\n'

        return result

    def formatIssues(self,issuesList):
        result='\\begin{description}[leftmargin=!,labelwidth=\\widthof{\\bfseries Issue 000}]\n'
        for eachIssue in issuesList:
            hrefIssue = '\\href{http://bugs.oe-f.org/view.php?id=' + eachIssue['id'] +' }{Issue ' + eachIssue['id'] + '}'
            result += '\\item[' + hrefIssue + ']  ' + eachIssue['summary'].replace('&','\&')
            result += '\n'

        result += '\\end{description}'
        return result

    def writeFileOnDisk(self,version,text):
        file = open(dirPath.latexWorkingDir + 'OpenBoard_'+version+'.tex','w')
        file.write(text.encode('utf8'))
        file.close()

    def updateTexDocument(self):
        file = open('titlePage.tex','r')
        titlePage = file.read()
        file.close()

        files = glob.glob(dirPath.latexWorkingDir + '/OpenBoard*.tex')
        for eachFile in sorted(files,reverse=True):
            resourceName = eachFile.replace(dirPath.latexWorkingDir,'')
            resourceName = resourceName.replace('.tex','')
            titlePage += '\\include{'+ resourceName +'}\n'

        titlePage += '\n\n'

        titlePage += '\\chapter*{Open-Sankore}\n'
        titlePage += '\\addcontentsline{toc}{chapter}{Open-Sankore}\n'
        titlePage += '\\includepdf[pages={-}]{sankore.pdf}\n'
        titlePage += '\\end{document}'

        file = open(dirPath.latexWorkingDir+'OpenBoardReleaseNote.tex','w')
        file.write(titlePage)
        file.close()

        shutil.copyfile('sankore.pdf',dirPath.latexWorkingDir+'sankore.pdf')


class XMLParser(object):
    def readFile(self,filePath):
        #open the xml file for reading:
        file = open(filePath,'r')
        #convert to string:
        data = file.read()
        #close file because we dont need it anymore:
        file.close()
        #parse the xml you got from the file
        dom = parseString(data)
        return dom

    def getValueFromName(self,domElement,tagName):
        value=domElement.getElementsByTagName(tagName)[0].toxml()
        return value.replace('<'+tagName+'>','').replace('</'+tagName+'>','')

    def issues(self,dom):
        xmlIssues = dom.getElementsByTagName('issue')
        issues = []
        for eachIssue in xmlIssues:
            issueId = self.getValueFromName(eachIssue,'id')
            issueSummary = self.getValueFromName(eachIssue,'summary')
            issueSummary = issueSummary.replace('&quot;','"')
            issues.append({'id':issueId,'summary':issueSummary})

        return issues


def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h",["help"])

        directories = dirPath()
        directories.cleanDirectoy(dirPath.latexWorkingDir)
        directories.checkDirectory(dirPath.latexWorkingDir)
        
        xmlParser = XMLParser()
        texFileBuilder=TexFileBuilder()
        files = glob.glob(dirPath.exportedXMLDir + '/*.xml')
        for eachFile in files:
            print eachFile
            version_and_date = eachFile.replace(dirPath.exportedXMLDir + "exported_issues_",'')
            version_and_date = version_and_date.replace('.xml','')
            splitted_text = version_and_date.split('_')
            version = splitted_text[0]
            date = splitted_text[1]
            dom = xmlParser.readFile(eachFile)
            #print xmlParser.issues(dom)
            fileText = texFileBuilder.headerOfFile(version, date)
            fileText += texFileBuilder.formatIssues(xmlParser.issues(dom))
            texFileBuilder.writeFileOnDisk(version,fileText)

        texFileBuilder.updateTexDocument()
        
        os.chdir(dirPath.latexWorkingDir)
        #the second call is necessary to build the pdf content
        subprocess.call(['pdflatex', 'OpenBoardReleaseNote.tex'])
        subprocess.call(['pdflatex', 'OpenBoardReleaseNote.tex'])
        os.chdir('..')        
        os.rename(dirPath.latexWorkingDir+'/OpenBoardReleaseNote.pdf', 'OpenBoardReleaseNote.pdf')
        
        sys.exit(0)

    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)



if __name__ == "__main__":
    main()
