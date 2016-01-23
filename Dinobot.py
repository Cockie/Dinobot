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


queue=[]
timers={'yay': 0, 'joshpost': 0, 'pudding': 0, 'python': 0, 'microsoft': 0, 'linux': 0}
shushed=False
online=True
confus=[]
with open('confucius.txt') as f:
   for line in f:
       print(line)
       line=line[line.find('.')+1:].strip()
       confus.append(line)

def decrtimer(dur):
    global timers
    for key in timers:
        timers[key]-=dur
        if timers[key]<0:
            timers[key]=0
            
def sleeping(dur):
    sleep(dur)
    decrtimer(dur)


# Some basic variables used to configure the bot        
server = "irc.web.gamesurge.net" # Server
channel = "#limittheory" # Channel
botnick = "Saoirse" # Your bots nick


def ping(mess): # This is our first function! It will respond to server Pings.
    ircsock.send(bytes('PONG %s\r\n' % mess, 'UTF-8'))

def sendmsg(chan , msg, delay=True): # This is the send message function, it simply sends messages to the channel.
    if delay: 
        time=len(msg)/50.0
        sleeping(1)
    ircsock.send(bytes("PRIVMSG "+ chan +" :"+ msg +"\n", 'UTF-8') )

def joinchan(chan): # This function is used to join channels.
    ircsock.send(bytes("JOIN "+ chan +"\n", 'UTF-8'))

def quitirc(): # This function is used to quit IRC entirely
    global online
    ircsock.send(bytes("QUIT "+" :PUDDING\n", 'UTF-8'))
    online=False
    
def leavechan(chan):
    ircsock.send(bytes("PART "+ chan+" :PUDDING\n", 'UTF-8'))
    
def hello(_channel,): # This function responds to a user that inputs "Hello Mybot"
    sendmsg(_channel, "Hello!")
    
def yay(_channel):
    global timers
    if timers['yay']<=0:
        sleeping(0.6)
        sendmsg(_channel, '\o/')
        timers['yay']=10
        
def pudding(_channel, small=False):
    global timers
    if timers['pudding']<=0:
        sleeping(0.6)
        if small:
            sendmsg(_channel, 'Pudding!')
        else:
            sendmsg(_channel, 'PUDDING!')
        timers['pudding']=10
        
def joshpost(_channel):
    global timers
    if timers['joshpost']<=0:
        sleeping(0.6)
        sendmsg(_channel, 'POSHJOST! \o/')
        timers['joshpost']=10
        
def microsoft(_channel):
    global timers
    if timers['microsoft']<=0:
        sleeping(0.6)
        sendmsg(_channel, "ACTION shakes fist at Microsoft")
        timers['microsoft']=500
        
def python(_channel):
    global timers
    if timers['python']<=0:
        sleeping(0.6)
        sendmsg(_channel, "Yay Python! \o/")
        timers['python']=500
        
def linux(_channel):
    global timers
    if timers['linux']<=0:
        sleeping(0.6)
        sendmsg(_channel, "Yay Linux! \o/")
        timers['linux']=500
        
def greet(_channel,mess):
    usr=mess[1:mess.find('!')]
    sendmsg(_channel, "Hey "+usr+"!")
    sendmsg(_channel, "o/")
def rektwiki(_channel,mess):
    r = request.urlopen("http://lt-rekt.wikidot.com/search:site/q/"+mess.strip().replace(' ','\%20'))
    htmlstr = r.read().decode().replace(' ','').replace('\t','').replace('\n','')
    htmlstr=htmlstr[htmlstr.find("<divclass=\"title\"><ahref=\""):].replace("<divclass=\"title\"><ahref=\"",'')
    htmlstr=htmlstr[:htmlstr.find("\""):].replace("\"",'')
    print(htmlstr+'\n')
    sendmsg(_channel, htmlstr)
    
def confucius(_channel):
    sendmsg(_channel, "Confucius says: "+random.choice(confus))
   
 
   
   
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
    testbool=False
    while read!="":  
        sendmsg(_channel, read.strip(), delay=testbool)
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
        
    
                  
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a result of a tutoral covered on http://shellium.org/wiki.\n", 'UTF-8')) # user authentication
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
def main():
    while online: # Be careful with these! it might send you to an infinite loop
        global shushed
        timer=time()
        ircmsg = ircsock.recv(2048) # receive data from the server
        try: buf=io.StringIO(str(ircmsg, encoding='utf-8').strip('\r'))
        except Exception: buf=io.StringIO("")
        while True:
            read=buf.readline()
            if read!="":
                queue.append(read)
            else: break
        while len(queue)!=0:
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
                if not shushed:     
                    if "what is love" in lmess:
                        sendmsg(_channel,"Oh baby, don't hurt me")
                        sendmsg(_channel,"Don't hurt me no more")  
                    if "\o/" in lmess and "taiya" not in lmess and "jimmy" not in lmess:                
                        yay(_channel,)
                    elif "rekt wiki" in lmess:
                        lmess=lmess[lmess.find("rekt wiki"):]
                        lmess=lmess.replace("rekt wiki",'').strip()
                        rektwiki(_channel,lmess)
                    elif "TABLEFLIP" in mess:
                        temp="︵ヽ(`Д´)ﾉ︵"
                        for i in range(1,lmess.count('!')):
                            temp+="  "
                            temp="  "+temp
                        temp+="┻━┻ "
                        print(temp)
                        temp="┻━┻ "+temp
                        print(temp)
                        sendmsg(_channel,temp) 
                    elif "tableflip" in lmess:
                        temp="(╯°□°）╯︵"
                        for i in range(1,lmess.count('!')):
                            temp+="  "
                        temp+="┻━┻ "
                        sendmsg(_channel,temp) 
                    elif "joshpost" in lmess: # if the server pings us then we've got to respond!
                        joshpost(_channel,)
                    
                    elif "pudding" in lmess:
                        pudding(_channel)
     
                    elif "microsoft" in lmess or "windows" in lmess:
                        microsoft(_channel)
                    elif "python" in lmess:
                        python(_channel)
                    elif "linux" in lmess:
                        linux(_channel)
                    elif "hail satan" in lmess:
                        sendmsg(_channel,"All hail the dark lord!! o/ His victory is certain!! o/")
                    elif re.search(regex1, lmess)!=None:
                        sendmsg(_channel,"DOOOOMED!")
                    elif re.search(regex2, lmess)!=None:
                        sendmsg(_channel,"SPAAACE!")
                    elif "whyy" in lmess:
                        sendmsg(_channel, "¯\_(ツ)_/¯")
                    elif "saoirse" in lmess:
                        if ("hello" in lmess) or ("hey" in lmess) or ("greetings" in lmess) or (" hi" in lmess) or ("hi saoirse" in lmess) or ("hi," in lmess): # if the server pings us then we've got to respond!
                            hello(_channel)
                        lmess=stripleft(lmess,"saoirse")
                        mess=stripleft(mess,"Saoirse")
                        print(lmess)
                        
                        if "join" in lmess:
                            tojoin=lmess[lmess.find("join"):].replace("join",'').strip()
                            joinchan(tojoin)
                            sendmsg(_channel, "To "+tojoin+" and beyond! /o/")
                        elif "leave" in lmess:
                            sendmsg(_channel, "Bye! o/")
                            leavechan(_channel)
                        elif "quit" in lmess:
                            sendmsg(_channel, "Bye! o/")
                            quitirc()
                        elif "help" in lmess:
                            sendmsg(_channel,"https://docs.google.com/document/d/12HqksZncFBCE-wKQuNAUtHwyYj9LqZQ9xe3hEP_AekQ/edit?usp=sharing")
                        elif "shush" in lmess:
                            sendmsg(_channel,"OK, I'll shut up :(")
                            shushed=True
                        elif "what is" in lmess:
                            lmess=lmess[lmess.find("wh"):]
                            wiki(_channel,stripleft(lmess,"what is"),3)
                        elif "what's" in lmess:
                            lmess=lmess[lmess.find("wh"):]
                            wiki(_channel,stripleft(lmess,"what's"),3)               
                        elif "whats" in lmess:
                            lmess=lmess[lmess.find("wh"):]
                            wiki(_channel,stripleft(lmess,"whats"),3)
                        elif "who's" in lmess:
                            lmess=lmess[lmess.find("wh"):]
                            wiki(_channel,stripleft(lmess,"who's"),3)
                        elif "who is" in lmess:
                            lmess=lmess[lmess.find("wh"):]
                            wiki(_channel,stripleft(lmess,"who is"),3)
                        elif "how do i" in lmess:
                            lmess=lmess[lmess.find("how"):]
                            wiki(_channel,stripleft(lmess,"how do i"),3)
                        elif "confuc" in lmess or "confusius" in lmess:
                            confucius(_channel)
                        else: pudding(_channel,small=True)
            elif "speak" in lmess:
                            sendmsg(_channel,"Yay! Pudding!")
                            shushed=False
                        
    
    
                
    
            del queue[0]
        timer-=time()
        timer=-timer
        decrtimer(timer)

_thread.start_new_thread(main,())
while True:
    inpsay()
