# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 21:09:34 2015

@author: yorick
"""



# Import some necessary libraries.
import socket 
import io
from time import *
import wikipedia
from urllib import request
import _thread
import sys
import random
import re
import subprocess

queue=[]
greetings=["hello", "hey", "hi", "greetings", "hoi"]
wikitriggers=["what is", "what's", "whats", "who's", "who is", "how do i"]
blacklist=[]
timers={}
triggers={}
timervals={}
shushed=False
online=True
broken=False
confus=[]
lefts=[]
rights=[]
eyes=[]
mouths=[]
emoticons={}
spacelist=[]     
# Some basic variables used to configure the bot        
server = "irc.web.gamesurge.net" # Server
channel = "#limittheory" # Channel
#channel = "#talstest" # Channel
botnick = "Saoirse" # Your bots nick

def stringify(t):
    res=""
    for stuff in t:
        res+=stuff
        res+=", "
    return res.strip(',')

def readblacklist():
    global blacklist
    blacklist=[]
    with open('blacklist.txt') as f:
        for line in f:
            blacklist.append(":"+line.strip())
    print(blacklist)

def writeblacklist():
    global blacklist
    f=open('blacklist.txt','w')
    for nick in blacklist:
        f.write(nick.strip(':')+'\n')
    f.close()
    print(blacklist)

def initialise():
    global spacelist
    global timers
    global triggers
    global timervals
    global confus
    global eyes
    global lefts
    global rights
    global mouths
    global emoticons
    global spacelist
    
    with open('space.txt') as f:
        for line in f:
            spacelist.append(line.strip().replace('"',''))
    timers['space']=0
    
    with open('confucius.txt') as f:
       for line in f:
           line=line[line.find('.')+1:].strip()
           confus.append(line)
           
    test="#LEFTS"
    with open('procemo.txt') as f:
        for line in f:
            line=line.strip('\n').strip(' ')
            if line=='':
                pass
            elif line.startswith('#'):
                test=line
            else:
                if test=="#LEFTS":
                    lefts.append(line)
                elif test=="#RIGHTS":
                    rights.append(line)
                elif test=="#EYES":
                    eyes.append(line)
                elif test=="#MOUTHS":
                    mouths.append(line)
    
    with open('emoticons.txt',encoding='utf-8') as f:
        for line in f:
            #print(line)
            line=line.strip('\n').strip(' ').split('&')
            if line[0]=='':
                pass
            else:
                emoticons[line[0]]=line[1]
    print("EMOTICONS")
    print(emoticons)
    with open('triggers.txt',encoding='utf-8') as f:
        for line in f:
            line=line.strip('\n').strip(' ').split('|')
            line[0]=line[0].split('&')
            if line[0][0]=='':
                pass
            else:
                triggers[tuple(line[0])]=line[1].replace("\\n",'\n')
                timers[line[0][0]]=0
                timervals[line[0][0]]=int(line[2])
    print("TRIGGERS")
    print(triggers)
                

    with open('README.md','w') as f:
        with open('read1.txt') as f1:
            for line in f1:
                f.write(line)
            for key in sorted(triggers):
                f.write(stringify(key)+": "+triggers[key]+"  \n")
        f.write("  \n")
        with open('read2.txt') as f1:
            for line in f1:
                f.write(line)
            for key in sorted(emoticons):
                f.write(key+": "+emoticons[key]+"  \n")
    readblacklist()

    push=False
    strout="Automatic update"
    output = subprocess.check_output(["git", "diff", "README.md"])
    print(output)
    if output!=b'': 
        push=True
        output = subprocess.call(["git","add", "README.md"], stdout=subprocess.PIPE)
        print(output)
        strout+=" README"
    output = subprocess.check_output(["git", "diff", "emoticons.txt"])
    print(output)
    if output!=b'': 
        push=True
        output = subprocess.call(["git","add", "emoticons.txt"], stdout=subprocess.PIPE)
        print(output)
        strout+=" emoticons"
    output = subprocess.check_output(["git", "diff", "triggers.txt"])
    print(output)
    if output!=b'': 
        push=True
        output = subprocess.call(["git","add", "triggers.txt"], stdout=subprocess.PIPE)
        print(output)
        strout+=" triggers"
    output = subprocess.check_output(["git", "diff", "blacklist.txt"])
    print(output)
    if output!=b'': 
        push=True
        output = subprocess.call(["git","add", "blacklist.txt"], stdout=subprocess.PIPE)
        print(output)
        strout+=" blacklist"
    if push:
        output = subprocess.call(["git","commit", "-m" ,strout], stdout=subprocess.PIPE)
        print(output)
        output = subprocess.call(["git", "push"], stdout=subprocess.PIPE)
        print(output)
    
    
        
                
def decrtimer(dur):
    global timers
    for key in timers:
        timers[key]-=dur
        if timers[key]<0:
            timers[key]=0
            
def sleeping(dur):
    sleep(dur)
    decrtimer(dur)

def procemo(chan):
    i=random.randint(1,6)
    test=random.choice(lefts)
    eye=random.choice(eyes)
    test+=eye
    test+=random.choice(mouths)
    if i==6:
        test+=random.choice(eyes)
    else:
        test+=eye
    test+=random.choice(rights)
    print(i)
    sendmsg(chan, test)
    
def ping(mess): # This is our first function! It will respond to server Pings.
    ircsock.send(bytes('PONG %s\r\n' % mess, 'UTF-8'))

def sendmsg(chan , msg, delay=True): # This is the send message function, it simply sends messages to the channel.
    if delay: 
        time=len(msg)/50.0
        sleeping(1)
    msg=msg.split('\n')
    for line in msg:
        ircsock.send(bytes("PRIVMSG "+ chan +" :"+ line +"\n", 'UTF-8') )

def pm(name , msg): # This is the send message function, it simply sends messages to the channel.
    ircsock.send(bytes("PRIVMSG " + name + " :" + msg + "\n", 'UTF-8'))

def joinchan(chan): # This function is used to join channels.
    ircsock.send(bytes("JOIN "+ chan +"\n", 'UTF-8'))

def quitirc(): # This function is used to quit IRC entirely
    global online
    ircsock.send(bytes("QUIT "+" :PUDDING\n", 'UTF-8'))
    online=False
    
def leavechan(chan):
    ircsock.send(bytes("PART "+ chan+" :PUDDING\n", 'UTF-8'))
         
def space(_channel):
    global timers
    if timers['space']<=0:
        sleeping(0.6)
        sendmsg(_channel, random.choice(spacelist))
        timers['space']=200
       
def greet(_channel,mess):
    usr=mess[1:mess.find('!')]
    sendmsg(_channel, "Hey "+usr+"!")
    sendmsg(_channel, "o/")
    
def rektwiki(_channel,mess):
    mess=mess[mess.find("rekt wiki"):]
    mess=mess.replace("rekt wiki",'').strip()
    r = request.urlopen("http://lt-rekt.wikidot.com/search:site/q/"+mess.strip().replace(' ','\%20'))
    htmlstr = r.read().decode().replace(' ','').replace('\t','').replace('\n','')
    htmlstr=htmlstr[htmlstr.find("<divclass=\"title\"><ahref=\""):].replace("<divclass=\"title\"><ahref=\"",'')
    htmlstr=htmlstr[:htmlstr.find("\""):].replace("\"",'')
    print(htmlstr+'\n')
    sendmsg(_channel, htmlstr)

def findtitle(_channel,mess):
    res=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', mess[mess.find(channel)+2:])
    print(res)
    req = request.Request(
    res[0], 
    data=None, 
    headers={
        'User-Agent': 'Chrome/35.0.1916.47'
    }
    )
    try:
        r = request.urlopen(req, timeout=1)
    except Exception:
        return
    print(r.geturl())
    htmlstr = r.read()
    try:
        htmlstr=htmlstr.decode()
    except Exception:
        htmlstr=str(htmlstr)
    htmlstr=htmlstr.replace('\t','').replace('\n','')
    print(htmlstr)
    #htmlstr=htmlstr.decode().replace('\t','').replace('\n','')
    #print(htmlstr)
    try:
        htmlstr=htmlstr[htmlstr.find("<title>"):].replace("<title>",'')
        htmlstr=htmlstr[:htmlstr.find("</title>"):].replace("</title>",'')
        print(htmlstr+'\n')
    except Exception:
        return
    if htmlstr!="":
        sendmsg(_channel, htmlstr.strip())
    
def confucius(_channel):
    sendmsg(_channel, "Confucius says: "+random.choice(confus))  

def listemo(_channel, mess):
    sendmsg(_channel, "I'll pm you.")
    user=mess[mess.find(":")+1:mess.find("!")]
    for key, value in emoticons.items():
        pm(user, key+": "+value)
   
def wiki(_channel,string, count):
    string=string.strip("'").strip('\r\n').strip("?").strip(".").strip("!").lower()
    string=string.strip()
    if string.startswith("a "):
        string=string[2:]
    elif string.startswith("an "):
        string=string[3:]
    elif string.startswith("the "):
        string=string[4:]
    print(string)
    try: 
        message=wikipedia.summary(string, sentences=count).replace('. ',".\n")
        pageresult=wikipedia.page(string).url.replace('Https://en.wikipedia.org/wiki/','').replace('https://en.wikipedia.org/wiki/','')
    except Exception:
        res = wikipedia.search(string)
        print(res)
        temppage=0
        pageresult=0 
        ref=0
        counter=0
        maxres=5
        test=wikipedia.suggest(string)
        print(test)
        if test== None or test.lower().replace(' ','')!=string.replace(' ',''):
            for stuff in res:
                print(stuff.lower().replace(' ','') )
                print(string.replace(' ',''))
                if stuff.lower().replace(' ','') == string.replace(' ','') : #exact match
                    pageresult=stuff
                    break
                else:
                    try: 
                        temppage=wikipedia.page(stuff)
                        if len(temppage.references)>ref:
                            ref=len(temppage.references)
                            pageresult=stuff
                        counter+=1
                        if counter>maxres:
                            break
                    except wikipedia.exceptions.DisambiguationError as e:
                        #print(e.options)
                        for opt in e.options:
                            try: 
                                temppage=wikipedia.page(opt)
                                if len(temppage.references)>ref:
                                    ref=len(temppage.references)
                                    pageresult=opt
                                counter+=1
                                if counter>maxres:
                                    break
                            except : 
                                pass
                    except KeyError:
                        pass
                    counter+=1
                    if counter>maxres:
                        break
        else:
            pageresult=test
            print(pageresult)
        try: message=wikipedia.summary(pageresult, sentences=count).replace('. ',".\n")
        except wikipedia.exceptions.DisambiguationError as e:
            sendmsg(_channel, "I'm not sure what you mean, i could find:", delay=False)
            i=0
            if count!=1:
                for stuff in e.options:
        
                        sendmsg(_channel, "https://en.wikipedia.org/wiki/"+stuff.replace(' ','_'))
                        message="That's all!"
                        i+=1
                        if i==count:
                            message="There's more but I'm stopping there!!"
                            break
            else:
                message="https://en.wikipedia.org/wiki/"+pageresult.replace(' ','_')
        except Exception as e: 
            print(e)
            message="Something went wrong. It's the fault of the python library makers!"
            sendmsg(_channel, message, delay=False)
            return
    buf=io.StringIO(str(message))
    read=buf.readline()
    print(read)
    testbool=False
    while read!="":  
        sendmsg(_channel, read.strip().replace('\n',''), delay=testbool)
        read=buf.readline()
        testbool=True
    if count!=1: sendmsg(_channel, "https://en.wikipedia.org/wiki/"+pageresult.replace(' ','_'))
        

def inpsay():
    cmd = sys.stdin.readline()
    if cmd!="":
        if cmd.startswith("/me"):
            string="ACTION"+cmd[3:].strip('\n')+""
            #print(string)
            sendmsg(channel,string)
        else:
            sendmsg(channel, cmd)
        
def stripleft(string, stuff):
    return string[string.find(stuff)+len(stuff):]
        
initialise()  
                  
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a result of a tutorial covered on http://shellium.org/wiki.\n", 'UTF-8')) # user authentication
ircsock.send(bytes("NICK "+ botnick +"\n", 'UTF-8')) # here we actually assign the nick to the bot

 # Join the channel using the functions we previously defined

while 1: # Be careful with these! it might send you to an infinite loop
    ircmsg = ircsock.recv(2048) # receive data from the server
    buf=io.StringIO(str(ircmsg))
    while True:
        read=buf.readline()
        if read!="":
            queue.append(read)
        else: break
    mess = queue[0] # removing any unnecessary linebreaks.
    mess = mess.strip('\n\r').strip()
    #print(mess) # Here we print what's coming from the server


    if mess.find("Found your hostname") != -1 or mess.find("No ident response") !=-1:
      
      sent="NICK "+ botnick +"\n"+"USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a result of a tutoral covered on http://shellium.org/wiki.\n"
      ircsock.send(bytes(sent, 'UTF-8')) # here we actually assign the nick to the bot
      print(sent)
      ircsock.send(bytes("PRIVMSG nickserv :iNOOPE\r\n", 'UTF-8'))

    if mess.find("Welcome to the GameSurge IRC") != -1: # if the server pings us then we've got to respond!
        break
    
    if mess.find("PING :") != -1: # if the server pings us then we've got to respond!
        ping(mess)
    
    if len(queue)!=0:
        del queue[0]
      
joinchan(channel)
del queue
queue=[]
print("yay")

def readirc(queue):
    global shushed
    global broken
    global timers
    mess = queue[0] # removing any unnecessary linebreaks.
    print(mess)
    test = mess.strip('\r\n').strip().strip("'")
    mess=test
    lmess=mess.lower()
    _channel=lmess[lmess.find("#"):]
    _channel=_channel[:_channel.find(":")].strip()
    regex1 = re.compile('do+omed')
    regex2 = re.compile('spa+ce')
    #print(_channel)
    if mess.find("PING :") != -1: # if the server pings us then we've got to respond!
        ping(mess)
    if "GameSurge" not in mess and lmess.find(":saoirse!")!=0: 
        if not shushed and not any([stuff in lmess for stuff in blacklist]):    
            if "saoirse" in lmess:
                if any([greeting in lmess for greeting in greetings]):
                    sendmsg(_channel, random.choice(greetings).title()+"!")     
                #lmess=stripleft(lmess,"saoirse")
                #mess=stripleft(mess,"Saoirse")
                print(lmess)
                if "join" in lmess:
                    tojoin=lmess[lmess.find("join"):].replace("join",'').strip()
                    joinchan(tojoin)
                    sendmsg(_channel, "To "+tojoin+" and beyond! /o/")
                    return
                elif "leave" in lmess:
                    sendmsg(_channel, "Bye! o/")
                    leavechan(_channel)
                    return
                elif "quit" in lmess:
                    sendmsg(_channel, "Bye! o/")
                    quitirc()
                    return
                elif "shush" in lmess:
                    sendmsg(_channel,"OK, I'll shut up :(")
                    shushed=True
                    return
                elif "initialise" in lmess or "initialize" in lmess:
                    sendmsg(_channel,"OK, reinitialising...")
                    initialise()
                    sendmsg(_channel,"Done! Should work now.")
                    return
                elif "deignore" in lmess and ":dinosawer" in lmess:
                    nick=lmess[lmess.find("deignore")+len("deignore"):].strip()
                    blacklist.remove(":"+nick)
                    writeblacklist()
                elif "ignore" in lmess and ":dinosawer" in lmess:
                    nick=lmess[lmess.find("ignore")+len("ignore"):].strip()
                    if nick!="dinosawer":
                        blacklist.append(":"+nick)
                        writeblacklist()
                #wikipedia search
                else:
                    for stuff in wikitriggers:
                        if stuff in lmess:
                            lmess=lmess[lmess.find(stuff):]
                            wiki(_channel,stripleft(lmess,stuff),3)
                            return
                if "confuc" in lmess or "confusius" in lmess:
                    confucius(_channel)
                    return
                else: sendmsg(_channel,"Pudding!")
            #no-named things
            if "rekt wiki" in lmess:
                rektwiki(_channel,lmess)
                return
            elif "TABLEFLIP" in mess:
                temp="︵ヽ(`Д´)ﾉ︵"
                for i in range(1,lmess.count('!')):
                    temp+="  "
                    temp="  "+temp
                temp+="┻━┻ "
                temp="┻━┻ "+temp
                sendmsg(_channel,temp) 
                return
            elif "tableflip" in lmess:
                temp="(╯°□°）╯︵"
                for i in range(1,lmess.count('!')):
                    temp+="  "
                temp+="┻━┻ "
                sendmsg(_channel,temp) 
                return
            for key, value in emoticons.items():
                if key in lmess:
                    sendmsg(_channel,value)
                    return  
            if re.search(regex1, lmess)!=None:
                sendmsg(_channel,"DOOOOMED!")
                return
            if re.search(regex2, lmess)!=None:
                space(_channel)
                return
            for key, value in triggers.items():
                if any([stuff in lmess for stuff in key]):
                    if timers[key[0]]<=0:
                        sleeping(0.6)
                        sendmsg(_channel, value)
                        timers[key[0]]=timervals[key[0]]
                        return
            if "!procemo" in lmess:
                procemo(_channel)
                return
            if "!listemo" in lmess or "!emoticonlist" in lmess:
                listemo(_channel, mess)
                return
            if "http://www.gamesurge.net/cms/spamServ" not in lmess and "imgur" not in lmess and len(re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', lmess[lmess.find(channel)+2:]))!=0:
                findtitle(_channel, mess)
                return
        elif "speak" in lmess and "saoirse" in lmess:
            sendmsg(_channel,"Yay! Pudding!")
            shushed=False    
            return
    return


def main():
    while online: # Be careful with these! it might send you to an infinite loop
        timer=time()
        ircmsg = ircsock.recv(2048) # receive data from the server
        try: buf=io.StringIO(str(ircmsg, encoding='utf-8').strip('\r'))
        except Exception: buf=io.StringIO("")
        while True:
            read=buf.readline()
            if read!="":
                queue.append(read)
            else: break
        timer-=time()
        timer=-timer
        decrtimer(timer)
        while len(queue)!=0:
            timer=time()
            readirc(queue)
            #print(timers)
            del queue[0]
            timer-=time()
            timer=-timer
            decrtimer(timer)
        sleeping(0.100)

_thread.start_new_thread(main,())
while online:
    inpsay()
