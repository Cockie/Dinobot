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
from collections import OrderedDict
import sys
import readline
import select
import html

queue = []
greetings = ["hello", "hey", "hi", "greetings", "hoi"]
wikitriggers = ["what is", "what's", "whats", "who's", "who is", "how do i"]
blacklist = []
timers = {}
triggers = OrderedDict()
bottriggers = {}
timervals = {}
shushed = False
online = True
broken = False
confus = []
lefts = []
rights = []
eyes = []
mouths = []
emoticons = {}
spacelist = []
# Some basic variables used to configure the bot
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "irc.web.gamesurge.net"  # Server
channel = []
botnick = "Saoirse"  # Your bots nick
username = ""
password = ""
auth = True
smartlander = False

def stringify(t):
    res = ""
    for stuff in t:
        res += stuff
        res += ", "
    return res.strip(',')


def readblacklist():
    global blacklist
    blacklist = []
    with open('blacklist.txt') as f:
        for line in f:
            blacklist.append(line.strip())
    print(blacklist)


def writeblacklist():
    global blacklist
    f = open('blacklist.txt', 'w')
    for nick in blacklist:
        f.write(nick.strip() + '\n')
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
    global username
    global password
    global auth

    with open('space.txt') as f:
        for line in f:
            spacelist.append(line.strip().replace('"', ''))
    timers['space'] = 0

    with open('confucius.txt') as f:
        for line in f:
            line = line[line.find('.') + 1:].strip()
            confus.append(line)

    test = "#LEFTS"
    with open('procemo.txt') as f:
        for line in f:
            line = line.strip('\n').strip(' ')
            if line == '':
                pass
            elif line.startswith('#'):
                test = line
            else:
                if test == "#LEFTS":
                    lefts.append(line)
                elif test == "#RIGHTS":
                    rights.append(line)
                elif test == "#EYES":
                    eyes.append(line)
                elif test == "#MOUTHS":
                    mouths.append(line)

    with open('emoticons.txt', encoding='utf-8') as f:
        for line in f:
            # print(line)
            line = line.strip('\n').strip(' ').split('&')
            if line[0] == '':
                pass
            else:
                emoticons[line[0]] = line[1].replace("\\n", '\n')
    print("EMOTICONS")
    print(emoticons)
    with open('triggers.txt', encoding='utf-8') as f:
        triggers = OrderedDict()
        for line in f:
            line = line.strip('\n').strip(' ').split('|')
            line[0] = line[0].split('&')
            if line[0][0] == '':
                pass
            else:
                triggers[tuple(line[0])] = line[1].replace("\\n", '\n')
                timers[line[0][0]] = 0
                timervals[line[0][0]] = int(line[2])
                bottriggers[line[0][0]] = True if line[3].replace("\\n", '\n') == 'T' else False
    print("TRIGGERS")
    print(triggers)

    with open('README.md', 'w') as f:
        with open('read1.txt') as f1:
            for line in f1:
                f.write(line)
            for key in sorted(triggers):
                f.write(stringify(key) + ": " + triggers[key] + "  \n")
        f.write("  \n")
        with open('read2.txt') as f1:
            for line in f1:
                f.write(line)
            for key in sorted(emoticons):
                f.write(key + ": " + emoticons[key] + "  \n")

    with open('autojoin.txt') as f:
        for line in f:
            channel.append(line.strip().replace('\n', ''))

    with open('auth.txt') as f:
        username = f.readline().strip().replace('\n', '')
        password = f.readline().strip().replace('\n', '')
        if username == "" or password == "":
            auth = False

    readblacklist()

    push = False
    strout = "Automatic update"
    output = subprocess.check_output(["git", "diff", "README.md"])
    print(output)
    if output != b'':
        push = True
        output = subprocess.call(["git", "add", "README.md"], stdout=subprocess.PIPE)
        print(output)
        strout += " README"
    output = subprocess.check_output(["git", "diff", "emoticons.txt"])
    print(output)
    if output != b'':
        push = True
        output = subprocess.call(["git", "add", "emoticons.txt"], stdout=subprocess.PIPE)
        print(output)
        strout += " emoticons"
    output = subprocess.check_output(["git", "diff", "triggers.txt"])
    print(output)
    if output != b'':
        push = True
        output = subprocess.call(["git", "add", "triggers.txt"], stdout=subprocess.PIPE)
        print(output)
        strout += " triggers"
    output = subprocess.check_output(["git", "diff", "blacklist.txt"])
    print(output)
    if output != b'':
        push = True
        output = subprocess.call(["git", "add", "blacklist.txt"], stdout=subprocess.PIPE)
        print(output)
        strout += " blacklist"
    if push:
        output = subprocess.call(["git", "commit", "-m", strout], stdout=subprocess.PIPE)
        print(output)
        output = subprocess.call(["git", "push"], stdout=subprocess.PIPE)
        print(output)


def decrtimer(dur):
    global timers
    for key in timers:
        timers[key] -= dur
        if timers[key] < 0:
            timers[key] = 0


def sleeping(dur):
    sleep(dur)
    decrtimer(dur)


def procemo(chan):
    i = random.randint(1, 6)
    test = random.choice(lefts)
    eye = random.choice(eyes)
    test += eye
    test += random.choice(mouths)
    if i == 6:
        test += random.choice(eyes)
    else:
        test += eye
    test += random.choice(rights)
    sendmsg(chan, test)


def ping(mess):  # This is our first function! It will respond to server Pings.
    ircsock.send(bytes('PONG %s\r\n' % mess, 'UTF-8'))


def sendmsg(chan, msg, delay=True):  # This is the send message function, it simply sends messages to the channel.
    if delay:
        time_ = len(msg) / 50.0
        sleeping(1)

    if smartlander:
        print("smartlander is here")
        print(msg)
        msg = msg.replace('🍮',"༼ ༽")
        print(msg)
    msg = msg.split('\n')
    for line in msg:
        print(chan + '\t' + '<' + botnick + '>' + '\t' + line.strip('\n'))
        ircsock.send(bytes("PRIVMSG " + chan + " :" + line + "\n", 'UTF-8'))


def pm(name, msg):  # This is the send message function, it simply sends messages to the channel.
    print("PM'd " + name + ": " + msg)
    ircsock.send(bytes("PRIVMSG " + name + " :" + msg + "\n", 'UTF-8'))


def joinchan(chan):  # This function is used to join channels.
    ircsock.send(bytes("JOIN " + chan + "\n", 'UTF-8'))

def printIRC(mess):
    #print(mess)
    mess = mess.strip('\n')
    usr = mess[mess.find(':'):mess.find('!')].strip(':')
    if "NOTICE" in mess:
        print("Notice from " + usr + ': ' + mess[mess.find("NOTICE ")+7:])
        return 0
    if "JOIN" in mess:
        chan = '#' + mess.split('#')[1].split()[0]
        print(chan+'\t'+usr+" joined "+chan)
        return 0
    if "PART" in mess:
        chan = '#' + mess.split('#')[1].split()[0]
        mess = mess.split('PART')[1]
        mess = mess[mess.find(':') + 1:].strip('\n')
        print(chan + '\t' + usr + " left " + chan+" ("+mess+")")
        return 0
    if "QUIT" in mess:
        mess = mess.split('QUIT')[1]
        mess = mess[mess.find(':') + 1:].strip('\n')
        print(chan + '\t' + usr + " quit "+"("+mess+")")
        return 0
    if "MODE" in mess:
        return 0
    if "NICK" in mess:
        mess = mess.split('NICK')[1]
        mess = mess[mess.find(':') + 1:].strip('\n')
        print('\t' + '\t' + usr + " is now known as " + mess)
        return 0

    try:
        chan = '#'+mess.split('#')[1].split()[0]
    except Exception:
        chan = "PM"
    try:
        mess = mess.split('PRIVMSG')[1]
    except Exception:
        print(mess)
        return
    mess = mess[mess.find(':')+1:].strip('\n')
    if "ACTION" in mess:
        print(chan + '\t' + '*' + usr +mess[1:len(mess)-2].strip().strip("ACTION"))
    else:
        print(chan+'\t'+'<'+usr+'>'+'\t'+mess)
    return chan, usr, mess



def quitirc():  # This function is used to quit IRC entirely
    global online
    ircsock.send(bytes("QUIT " + " :PUDDING\n", 'UTF-8'))
    online = False


def leavechan(chan):
    ircsock.send(bytes("PART " + chan + " :PUDDING\n", 'UTF-8'))


def space(_channel):
    global timers
    if timers['space'] <= 0:
        sleeping(0.6)
        sendmsg(_channel, random.choice(spacelist))
        timers['space'] = 200


def greet(_channel, mess):
    usr = mess[1:mess.find('!')]
    sendmsg(_channel, "Hey " + usr + "!")
    sendmsg(_channel, "o/")


def rektwiki(_channel, mess):
    mess = mess[mess.find("rekt wiki"):]
    mess = mess.replace("rekt wiki", '').strip()
    try:
        r = request.urlopen("http://lt-rekt.wikidot.com/search:site/q/" + mess.strip().replace(' ', '\%20'))
    except Exception:
        return
    htmlstr = r.read().decode().replace(' ', '').replace('\t', '').replace('\n', '')
    htmlstr = htmlstr[htmlstr.find("<divclass=\"title\"><ahref=\""):].replace("<divclass=\"title\"><ahref=\"", '')
    htmlstr = htmlstr[:htmlstr.find("\""):].replace("\"", '')
    #print(htmlstr + '\n')
    sendmsg(_channel, htmlstr)


def findtitle(_channel, mess):
    res = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                     mess)
    #print(res)
    req = request.Request(
        res[0],
        data=None,
        headers={
            'User-Agent': 'Chrome/35.0.1916.47'
        }
    )
    try:
        r = request.urlopen(req, timeout=15)
    except Exception:
        return
    #print(r.geturl())
    htmlstr = r.read()
    try:
        htmlstr = htmlstr.decode()
    except Exception:
        htmlstr = str(htmlstr)
    htmlstr = htmlstr.replace('\t', '').replace('\n', '')
    #print(htmlstr)
    # htmlstr=htmlstr.decode().replace('\t','').replace('\n','')
    # print(htmlstr)
    try:
        htmlstr = htmlstr[htmlstr.find("<title>"):].replace("<title>", '')
        htmlstr = htmlstr[:htmlstr.find("</title>"):].replace("</title>", '')
        #print(htmlstr + '\n')
    except Exception:
        return
    if htmlstr != "":
        sendmsg(_channel, html.unescape(htmlstr.strip()))


def confucius(_channel):
    sendmsg(_channel, "Confucius says: " + random.choice(confus))


def listemo(_channel, user, mess):
    sendmsg(_channel, "I'll pm you.")
    user = user.strip('>').strip('<')
    m = ""
    i = 0
    for key, value in emoticons.items():
        m += key + ": " + value + "     "
        i += 1
        if i == 5:
            pm(user, m)
            m = ""
            i = 0
            sleeping(2)
    pm(user, "Done!")


def wiki(_channel, string, count):
    string = string.strip("'").strip('\r\n').strip("?").strip(".").strip("!").lower()
    string = string.strip()
    if string.startswith("a "):
        string = string[2:]
    elif string.startswith("an "):
        string = string[3:]
    elif string.startswith("the "):
        string = string[4:]
    print(string)
    try:
        message = wikipedia.summary(string, sentences=count).replace('. ', ".\n")
        pageresult = wikipedia.page(string).url.replace('Https://en.wikipedia.org/wiki/', '').replace(
            'https://en.wikipedia.org/wiki/', '')
    except Exception:
        res = wikipedia.search(string)
        print(res)
        temppage = 0
        pageresult = 0
        ref = 0
        counter = 0
        maxres = 5
        test = wikipedia.suggest(string)
        print(test)
        if test is None or test.lower().replace(' ', '') != string.replace(' ', ''):
            for stuff in res:
                print(stuff.lower().replace(' ', ''))
                print(string.replace(' ', ''))
                if stuff.lower().replace(' ', '') == string.replace(' ', ''):  # exact match
                    pageresult = stuff
                    break
                else:
                    try:
                        temppage = wikipedia.page(stuff)
                        if len(temppage.references) > ref:
                            ref = len(temppage.references)
                            pageresult = stuff
                        counter += 1
                        if counter > maxres:
                            break
                    except wikipedia.exceptions.DisambiguationError as e:
                        # print(e.options)
                        for opt in e.options:
                            try:
                                temppage = wikipedia.page(opt)
                                if len(temppage.references) > ref:
                                    ref = len(temppage.references)
                                    pageresult = opt
                                counter += 1
                                if counter > maxres:
                                    break
                            except:
                                pass
                    except KeyError:
                        pass
                    counter += 1
                    if counter > maxres:
                        break
        else:
            pageresult = test
            print(pageresult)
        try:
            message = wikipedia.summary(pageresult, sentences=count).replace('. ', ".\n")
        except wikipedia.exceptions.DisambiguationError as e:
            sendmsg(_channel, "I'm not sure what you mean, i could find:", delay=False)
            i = 0
            if count != 1:
                for stuff in e.options:

                    sendmsg(_channel, "https://en.wikipedia.org/wiki/" + stuff.replace(' ', '_'))
                    message = "That's all!"
                    i += 1
                    if i == count:
                        message = "There's more but I'm stopping there!!"
                        break
            else:
                message = "https://en.wikipedia.org/wiki/" + pageresult.replace(' ', '_')
        except Exception as e:
            print(e)
            message = "Something went wrong. It's the fault of the python library makers!"
            sendmsg(_channel, message, delay=False)
            return
    buf = io.StringIO(str(message))
    read = buf.readline()
    print(read)
    testbool = False
    while read != "":
        sendmsg(_channel, read.strip().replace('\n', ''), delay=testbool)
        read = buf.readline()
        testbool = True
    if count != 1:
        sendmsg(_channel, "https://en.wikipedia.org/wiki/" + pageresult.replace(' ', '_'))


def inpsay():
    #cmd = sys.stdin.readline()
    global queue
    cmd = input('> ').strip()
    if cmd != "":
        if cmd.startswith("/me"):
            string = "ACTION" + cmd[3:].strip('\n') + ""
            # print(string)
            sendmsg(channel[0], string)
        elif cmd.startswith("/msg"):
            pm(cmd.strip().split()[1], ' '.join(cmd.strip().split()[2:]))
        elif cmd.startswith("!"):
            queue.insert(0,":Dinosawer!Dinosawer@Dinosawer.user.gamesurge PRIVMSG "+channel[0]+" :"+cmd)
        else:
            sendmsg(channel[0], cmd)


def stripleft(string, stuff):
    return string[string.find(stuff) + len(stuff):]


def blacklisted(user):
    global blacklist
    return any([ stuff in user.lower() for stuff in blacklist])


def connect():
    global queue
    global ircsock
    # Here we connect to the server using the port 6667
    connected = False
    while not connected:
        try:
            ircsock.connect((server, 6667))
            connected = True
        except Exception:
            connected = False
            sleeping(5)
    ircsock.settimeout(180)
    ircsock.send(bytes(
        "USER " + botnick + " " + botnick + " " + botnick + " :This is a result of a tutorial covered on http://shellium.org/wiki.\n",
        'UTF-8'))  # user authentication
    ircsock.send(bytes("NICK " + botnick + "\n", 'UTF-8'))  # here we actually assign the nick to the bot
    while 1:  # Be careful with these! it might send you to an infinite loop
        ircmsg = ircsock.recv(2048)  # receive data from the server
        buf = io.StringIO(str(ircmsg))
        while True:
            read = buf.readline()
            if read != "":
                queue.append(read)
            else:
                break
        mess = queue[0]  # removing any unnecessary linebreaks.
        mess = mess.strip('\n\r').strip()
        # print(mess) # Here we print what's coming from the server
        if mess.find("Found your hostname") != -1 or mess.find("No ident response") != -1:
            sent = "NICK " + botnick + "\n" + "USER " + botnick + " " + botnick + " " + botnick + " :This is a result of a tutoral covered on http://shellium.org/wiki.\n"
            ircsock.send(bytes(sent, 'UTF-8'))  # here we actually assign the nick to the bot
            print(sent)
        if mess.find("Welcome to the GameSurge IRC") != -1:  # if the server pings us then we've got to respond!
            break
        if mess.find("PING :") != -1:  # if the server pings us then we've got to respond!
            ping(mess)
        if len(queue) != 0:
            del queue[0]
    # Join the channel using the functions we previously defined 
    if auth:
        pm("AuthServ@Services.GameSurge.net", "AUTH " + username + " " + password)
    for chan in channel:
        joinchan(chan)
    del queue
    queue = []
    print("yay")


initialise()
connect()


def readirc():
    global shushed
    global broken
    global timers
    global queue
    global botnick
    global bottriggers
    global triggers
    global smartlander
    mess = queue[0]  # removing any unnecessary linebreaks.
    if mess.find("PING :") != -1:  # if the server pings us then we've got to respond!
        ping(mess)
        return
    elif "Prothid.NY.US.GameSurge.net" in mess:
        return
    if "+smartlander" in mess:
        smartlander = True
    elif ":smartlander" in mess:
        if "QUIT" in mess:
            smartlander = False
        else:
            smartlander = True
    try:
        _channel, user, mess=printIRC(mess)
    except Exception:
        #some weird message?
        return
    """test = mess.strip('\r\n').strip().strip("'")
    mess = test"""
    lmess = mess.lower()
    """ _channel = lmess[lmess.find("#"):]
    _channel = _channel[:_channel.find(":")].strip()"""
    regex1 = re.compile('do+omed')
    regex2 = re.compile('spa+ce')
    # print(_channel)
    if "GameSurge" not in mess and user != botnick:
        if not shushed:
            if not blacklisted(user):
                if "saoirse" in lmess:
                    if any([greeting in lmess for greeting in greetings]):
                        sendmsg(_channel, random.choice(greetings).title() + "!")
                        # lmess=stripleft(lmess,"saoirse")
                    # mess=stripleft(mess,"Saoirse")
                    #print(lmess)
                    if "join" in lmess:
                        tojoin = lmess[lmess.find("join"):].replace("join", '').strip()
                        channel.append(tojoin)
                        joinchan(tojoin)
                        sendmsg(_channel, "To " + tojoin + " and beyond! /o/")
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
                        sendmsg(_channel, "OK, I'll shut up :(")
                        shushed = True
                        return
                    elif "initialise" in lmess or "initialize" in lmess:
                        sendmsg(_channel, "OK, reinitialising...")
                        initialise()
                        sendmsg(_channel, "Done! Should work now.")
                        return
                    elif "deignore" in lmess and "Dinosawer" in user:
                        nick = lmess[lmess.find("deignore") + len("deignore"):].strip()
                        blacklist.remove(nick)
                        writeblacklist()
                    elif "ignore" in lmess and "Dinosawer" in user:
                        nick = lmess[lmess.find("ignore") + len("ignore"):].strip()
                        if nick != "dinosawer":
                            blacklist.append(nick)
                            writeblacklist()
                    # wikipedia search
                    else:
                        for stuff in wikitriggers:
                            if stuff in lmess:
                                lmess = lmess[lmess.find(stuff):]
                                wiki(_channel, stripleft(lmess, stuff), 3)
                                return
                    if "confuc" in lmess or "confusius" in lmess:
                        confucius(_channel)
                        return
                    else:
                        sendmsg(_channel, "Pudding!")
                # no-named things
                if "rekt wiki" in lmess:
                    rektwiki(_channel, lmess)
                    return
                elif "TABLEFLIP" in mess:
                    temp = "︵ヽ(`Д´)ﾉ︵"
                    for i in range(1, lmess.count('!')):
                        temp += "  "
                        temp = "  " + temp
                    temp += "┻━┻ "
                    temp = "┻━┻ " + temp
                    sendmsg(_channel, temp)
                    return
                elif "tableflip" in lmess:
                    temp = "(╯°□°）╯︵"
                    for i in range(1, lmess.count('!')):
                        temp += "  "
                    temp += "┻━┻ "
                    sendmsg(_channel, temp)
                    return
                for key, value in emoticons.items():
                    if key in lmess:
                        sendmsg(_channel, value)
                        return
                if re.search(regex1, lmess) is not None:
                    sendmsg(_channel, "DOOOOMED!")
                    return
                if re.search(regex2, lmess) is not None:
                    space(_channel)
                    return
                if "!procemo" in lmess:
                    procemo(_channel)
                    return
                if "!listemo" in lmess or "!emoticonlist" in lmess:
                    listemo(_channel, user, mess)
                    return

                if "http://www.gamesurge.net/cms/spamServ" not in lmess and len(
                        re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                   lmess)) != 0:
                    findtitle(_channel, mess)
                    return
            for key, value in triggers.items():
                if any([stuff in lmess for stuff in key]):
                    if timers[key[0]] <= 0 and (not blacklisted(user) or bottriggers[key[0]]):
                        sleeping(0.6)
                        sendmsg(_channel, value)
                        timers[key[0]] = timervals[key[0]]
                        return

        elif "speak" in lmess and "saoirse" in lmess:
            sendmsg(_channel, "Yay! Pudding!")
            shushed = False
            return
    return


def main():
    global ircsock
    #ircsock.setblocking(0)
    while online:  # Be careful with these! it might send you to an infinite loop
        timer = time()
        received = True
        # print("receiving...")
        ready = select.select([ircsock], [], [], 1)
        if ready[0]:
            try:
                ircmsg = ircsock.recv(2048)  # receive data from the server
                received = True
            except Exception:
                received = False
            if not received or len(ircmsg) == 0:
                print("Disconnected!")
                connect()
            else:
                try:
                    buf = io.StringIO(str(ircmsg, encoding='utf-8').strip('\r'))
                except Exception:
                    buf = io.StringIO("")
                while True:
                    read = buf.readline()
                    if read != "":
                        queue.append(read)
                    else:
                        break
        timer -= time()
        timer = -timer
        decrtimer(timer)
        while len(queue) != 0:
            timer = time()
            sys.stdout.write('\r' + ' ' * (len(readline.get_line_buffer()) + 2) + '\r')
            readirc()
            sys.stdout.write('> ' + readline.get_line_buffer())
            sys.stdout.flush()
            # print(timers)
            del queue[0]
            timer -= time()
            timer = -timer
            decrtimer(timer)
        sleeping(0.100)


_thread.start_new_thread(main, ())
while online:
    inpsay()

