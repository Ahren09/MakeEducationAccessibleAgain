

import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client 
from apscheduler.schedulers.blocking import BlockingScheduler
import apscheduler

__author__ = "Connor Hennen"

#These are our credentials on Twilio for classNotifierService@gmail.com 
accountSID = 'ACe3c17e50096328c00dcab93158322f1d' 
authToken = '2ac8a397db0d1bde24c2f7f2ade3a325'
client = Client(accountSID, authToken)
classToUserDict = {}


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
    m61 = url
    r = requests.get(m61)
    content = r.content
    soup = BeautifulSoup(content)
    openC = soup.find("div",{"id":"enrl_mtng_info","class":"panel-7 overflow-autoScroll"})
    
    if re.search(r'Open',openC.text):
        openinfo = str(re.findall(r'(?=Open).+?(?<=Left)',openC.text)[0])
    elif re.search(r'0 of', openC.text):
        openinfo = str(re.findall(r'(?=0 of).+?(?<=Taken)',openC.text)[0])
    else:
        openinfo = ''
        
    return openinfo
    

def sendMessage():
    '''
    Function that texts ppl & deletes that number for that class afterwards
    '''
    global classToUserDict
    classToUserDict1 = classToUserDict.copy()
    
    checks = []
    checkToClassURL = {}
    for c in classToUserDict1:
        class1 = checkEnrollment(c)
        checks.append(checkEnrollment(c))
        checkToClassURL[class1] = c
        
    for i in range(0,len(checks)):

        if checks[i]: 
            for j in range(len(classToUserDict1[checkToClassURL[checks[i]]])): #So it texts all the people registered for that course
                message = client.messages.create(to=classToUserDict1[checkToClassURL[checks[i]]][j],from_="+17072101477", body= checks[i])
                del classToUserDict1[checkToClassURL[checks[i]]][j]


connor = "+17073277984"
rios = "+16194149537"
addClass('https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=181&subj_area_cd=MATH%20%20%20&crs_catlg_no=0061%20%20%20%20&class_id=262268910&class_no=%20001%20%20',connor)
addClass('https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=181&subj_area_cd=MATH%20%20%20&crs_catlg_no=0115A%20%20%20&class_id=262398910&class_no=%20001%20%20',connor)
addClass('https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=181&subj_area_cd=MATH%20%20%20&crs_catlg_no=0061%20%20%20%20&class_id=262268910&class_no=%20001%20%20',rios)
addClass('https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=181&subj_area_cd=MATH%20%20%20&crs_catlg_no=0115A%20%20%20&class_id=262398910&class_no=%20001%20%20',rios)

scheduler = BlockingScheduler()
scheduler.add_job(sendMessage, 'interval', seconds = 5) #This will make it query the site every five seconds and in the case that there are openings will also text every five seconds
scheduler.start()
