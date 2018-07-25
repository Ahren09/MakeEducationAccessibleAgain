#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 00:44:38 2018

@author: connorvhennen
"""

#Depencies: Python 2.7, twilio, apscheduler, internet, a twilio account,
#registered numbers on that account

#Twilio login info:
#E-mail: classNotifierService@gmail.com
#password: kangarookangaroo

#pip install twilio
from twilio.rest import Client 
import urllib2
import re
import copy
#conda install -c conda-forge apscheduler 
from apscheduler.schedulers.blocking import BlockingScheduler
import apscheduler
#Create a Twilio Account and set SID and Token to the values assigned to your account

#These are our credentials on Twilio for classNotifierService@gmail.com 
accountSID = 'ACe3c17e50096328c00dcab93158322f1d' 
authToken = '2ac8a397db0d1bde24c2f7f2ade3a325'
client = Client(accountSID, authToken)



def addClass(url,userNum):
    '''
    Function to connect course URLs to user phone numbers in the global 
    classToUserDict dict variable
    
    Param1: Course URL from UCLA Schedule of Classes
    Param2: Phone number of user who's registering for notifications for this course
    
    Return: None
    '''
    
    global classToUserDict
    #If the dict is has no key for this course, then the only value for that 
    #key will be the value added by this function
    if url not in classToUserDict:
        classToUserDict[url] = [userNum]
    #If the dict is has a key for this course, then the values will include all
    #phone numbers that have registered for this course
    else:
        classToUserDict[url].append(userNum)


def checkEnrollment(url):
    '''
    Function to check enrollment for a course URL
    
    Param1: 
        Course URL
    
    Return: 
        If spots are open, will return "There are y of z spots remaining in: course_title
        Otherwise will return 'The waitlist for class_name is either full or open(?)
    '''
    
    
    page=urllib2.urlopen(url).read()
    page = str(page)
    if re.search(r'Open',page):
        page1 = page.split('Open:')
        page2 = page1[1].split(' Left')
        page2[0] = re.sub(" ","",page2[0])

        spots = page2[0].split('of')

        clas = copy.deepcopy(page)
        
        clas = re.sub("real-time","",clas)
        clas = re.sub("\s+"," ",clas)
        clas = clas.split("Lecture")
        clas = clas[0].split("Summer 2018")
        classTitle= re.sub(r'<.+?>','',clas[1])
        classTitle= re.sub(r'  ',' ',classTitle)
        return "There are " + spots[0] + " of " + spots[1] + " spots remaining in: " +  classTitle[:-1]

    else:
        clas = copy.deepcopy(page)
        
        clas = re.sub("real-time","",clas)
        clas = re.sub("\s+"," ",clas)
        clas = clas.split("Lecture")
        clas = clas[0].split("Summer 2018")

        classTitle= re.sub(r'<.+?>','',clas[1])
        classTitle= re.sub(r'  ',' ',classTitle)
        if re.search('Closed',page):
            page1 = page.split('Closed')[1]
            page2 = page1.split(' span3')[0]
            waitlistSec = re.findall(r'<div.+?</div>',page2)[0]
            waitlist = re.findall(r'(?=<p>).+?(?<=</p>)',waitlistSec)[0]
            waitlist = re.sub(r'<.+?>','',waitlist)
        elif re.search('Waitlist',page):
            page1 = page.split('Class Full')[1]
            page2 = page1.split(' span3')[0]
            waitlistSec = re.findall(r'<div.+?</div>',page2)[0]
            waitlist = re.findall(r'(?=<p>).+?(?<=</p>)',waitlistSec)[0]
            waitlist = re.sub(r'<.+?>','',waitlist)
        return 'The waitlist for ' +  classTitle[:-1] + ' is: ' + waitlist



def sendMessage():
    '''
    Function that texts ppl. Im rly tired.
    '''
    global classToUserDict

    
    
    result = []
    checks = []
    checkToClassURL = {}
    for c in classToUserDict:
        class1 = checkEnrollment(c)
        checks.append(class1)
        checkToClassURL[class1] = c
        
    for i in range(0,len(checks)):
        print checks[i]
        if 'Waitlist Full' in checks[i] or 'No Waitlist' in checks[i]:
            a = 1
        else: 
            if len(result) > 0:
                result.append(checks[i])
            else:
                result.append(checks[i])
        if len(result[i])!=0:
            for j in range(len(classToUserDict[checkToClassURL[checks[i]]])): #So it texts all the people registered for that course
                message = client.messages.create(to=classToUserDict[checkToClassURL[checks[i]]][j],from_="+17072101477", body= result[i])

#Global variable, will store class urls as keys, and user phone numbers as values
classToUserDict = {}

connor = "+17073277984"
rios = "+16194149537"
addClass('https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=181&subj_area_cd=MATH%20%20%20&crs_catlg_no=0061%20%20%20%20&class_id=262268910&class_no=%20001%20%20',connor)
addClass('https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=181&subj_area_cd=MATH%20%20%20&crs_catlg_no=0115A%20%20%20&class_id=262398910&class_no=%20001%20%20',connor)
addClass('https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=181&subj_area_cd=MATH%20%20%20&crs_catlg_no=0061%20%20%20%20&class_id=262268910&class_no=%20001%20%20',rios)
addClass('https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=181&subj_area_cd=MATH%20%20%20&crs_catlg_no=0115A%20%20%20&class_id=262398910&class_no=%20001%20%20',rios)
sendMessage()

scheduler = BlockingScheduler()
scheduler.add_job(sendMessage, 'interval', seconds = 5) #This will make it query the site every five seconds and in the case that there are openings will also text every five seconds
scheduler.start()
