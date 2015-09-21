# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 21:09:34 2015

@author: yorick
"""

# Import some necessary libraries.
import socket 
import StringIO
from time import *
import wikipedia

queue=[]
timers={'yay': 0, 'joshpost': 0}
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
channel = "#talstest" # Channel
botnick = "Saoirse" # Your bots nick


def ping(mess): # This is our first function! It will respond to server Pings.
    ircsock.send("PONG"+mess.strip("PING")+'\n')  

def sendmsg(chan , msg, delay=True): # This is the send message function, it simply sends messages to the channel.
    if delay: 
        time=len(msg)/25.0
        sleeping(time)
    ircsock.send("PRIVMSG "+ chan +" :"+ msg +"\n") 

def joinchan(chan): # This function is used to join channels.
    ircsock.send("JOIN "+ chan +"\n")

def hello(): # This function responds to a user that inputs "Hello Mybot"
    sendmsg(channel, "Hello!")
    
def yay():
    global timers
    if timers['yay']<=0:
        sleeping(0.6)
        sendmsg(channel, '\o/')
        timers['yay']=5
        
def joshpost():
    global timers
    if timers['joshpost']<=0:
        sleeping(0.6)
        sendmsg(channel, 'POSHJOST! \o/')
        timers['joshpost']=5
        
def greet(mess):
    usr=mess[1:mess.find('!')]
    sendmsg(channel, "Hey "+usr+"!")
    sendmsg(channel, "o/")
    
def wiki(string):
    string=string.strip("?").strip(".").strip("!")
    res = wikipedia.search(string)
    print(res)
    temppage=0
    pageresult=0 
    ref=0
    counter=0
    maxres=10
    for stuff in res:
        try: 
            temppage=wikipedia.page(stuff)
            if len(temppage.references)>ref:
                ref=len(temppage.references)
                pageresult=stuff
            counter+=1
            if counter>maxres:
                break
        except wikipedia.exceptions.DisambiguationError as e:
            print e.options
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
    message=wikipedia.summary(pageresult, sentences=3).replace('.',".\n")
    buf=StringIO.StringIO(message)
    read=buf.readline()
    testbool=False
    while read!="":  
        sendmsg(channel, read.strip(), delay=testbool)
        read=buf.readline()
        testbool=True
    sendmsg(channel, "https://en.wikipedia.org/wiki/"+pageresult.replace(' ','_'))
    
                  
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
ircsock.send("NICK "+ botnick +"\n") # here we actually assign the nick to the bot

 # Join the channel using the functions we previously defined

while 1: # Be careful with these! it might send you to an infinite loop
    ircmsg = ircsock.recv(2048) # receive data from the server
    buf=StringIO.StringIO(ircmsg)
    while True:
        read=buf.readline()
        if read!="":
            queue.append(read)
        else: break
    mess = queue[0] # removing any unnecessary linebreaks.
    mess = mess.strip('\n\r').strip()
    print(mess) # Here we print what's coming from the server


    if mess.find("Found your hostname") != -1 or mess.find("No ident response") !=-1:
      
      sent="NICK "+ botnick +"\n"+"USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a result of a tutoral covered on http://shellium.org/wiki.\n"
      ircsock.send(sent) # here we actually assign the nick to the bot
      print(sent)
      ircsock.send("PRIVMSG nickserv :iNOOPE\r\n")

    if mess.find("Welcome to the GameSurge IRC") != -1: # if the server pings us then we've got to respond!
        break
    
    if mess.find("PING :") != -1: # if the server pings us then we've got to respond!
        ping(mess)
    
    if len(queue)!=0:
        del queue[0]
      
joinchan("#talstest")
del queue
queue=[]
print("yay")
while 1: # Be careful with these! it might send you to an infinite loop
    timer=time()
    ircmsg = ircsock.recv(2048) # receive data from the server
    buf=StringIO.StringIO(ircmsg)
    while True:
        read=buf.readline()
        if read!="":
            queue.append(read)
        else: break
    while len(queue)!=0:
        mess = queue[0] # removing any unnecessary linebreaks.
        mess = mess.strip('\n\r').strip()
        lmess=mess.lower()
        print(mess) # Here we print what's coming from the server
        if mess.find("PING :") != -1: # if the server pings us then we've got to respond!
            ping(mess)
        if "GameSurge" not in mess and lmess.find(":saoirse!")!=0:      
            if "saoirse" in lmess:
                if ("hello" in lmess) or ("hey" in lmess) or ("greetings" in lmess) or (" hi" in lmess) or ("hi saoirse" in lmess) or ("hi," in lmess): # if the server pings us then we've got to respond!
                    hello()
                    
                else: sendmsg(channel, "Pudding!")
                
            if mess.find("\o/") != -1: # if the server pings us then we've got to respond!
                yay()
                
            if mess.find("joshpost") != -1: # if the server pings us then we've got to respond!
                joshpost()
            
            if "join" in lmess:
                greet(mess)
            
            if "pudding" in lmess:
                sendmsg(channel, "PUDDING!")
                
            if "what is" in lmess:
                lmess=lmess[lmess.find("wh"):]
                wiki(lmess.strip("what is"))
            if "what's" in lmess:
                lmess=lmess[lmess.find("wh"):]
                wiki(lmess.strip("what's") )               
            if "whats" in lmess:
                lmess=lmess[lmess.find("wh"):]
                wiki(lmess.strip("whats"))
            if "how do i" in lmess:
                lmess=lmess[lmess.find("how"):]
                wiki(lmess.strip("how do i"))
                
            if "microsoft" in lmess or "windows" in lmess:
                sendmsg(channel, "ACTION shakes fist at Microsoft")
            if "whyy" in lmess:
                sendmsg(channel, "¯\_(ツ)_/¯")

            

        del queue[0]
    timer-=time()
    timer=-timer
    decrtimer(timer)
