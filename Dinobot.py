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
from urllib import parse
from urllib import error
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
import tailer
import datetime
import requests
import traceback
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

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
forumusername = ""
forumpw = ""
auth = True
smartlander = False
logmax = 10000
session = requests.Session()
rekturl = ""


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

def logerror(error):
    message = str(error) + '\n' + traceback.format_exc()
    message = message.splitlines()
    f = open('error.txt', 'a')
    f.write("[" + strftime("%d/%m/%Y %H:%M:%S") + "] " + '\n')
    for line in message:
        f.write(line.strip('\n') + '\n')
    f.write("------------------------------")
    f.close()

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
    global forumusername
    global forumpw
    global auth
    global session
    global rekturl
    with open('rekt.txt') as f:
        line = f.readline()
        line = line.strip('\n').strip()
        rekturl = line
    with open('space.txt') as f:
        for line in f:
            spacelist.append(line.strip().replace('"', ''))
    timers['space'] = 0
    timers['shushed'] = 0

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

    with open('emoticons.txt') as f:
        for line in f:
            # print(line)
            line = line.strip('\n').strip(' ').split('&')
            if line[0] == '':
                pass
            else:
                emoticons[line[0]] = line[1].replace("\\n", '\n')
    #print("EMOTICONS")
    #print(emoticons)
    with open('triggers.txt') as f:
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
    #print("TRIGGERS")
    #print(triggers)

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
        forumusername = f.readline().strip().replace('\n', '')
        forumpw = f.readline().strip().replace('\n', '')
        if username == "" or password == "":
            auth = False
    head = {'User-Agent': 'Chrome/35.0.1916.47'}
    if forumusername != "" and forumpw != "":
        url = "http://forums.ltheory.com/ucp.php?mode=login"
        payload = {"username": forumusername, \
                   "password": forumpw, \
                   'redirect': 'index.php', \
                   'sid': '', \
                   'login': 'Login'}
        try:
            p = session.post(url, headers=head, data=payload, timeout=15)
        except Exception as e:
            logerror(e)

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
    global connected
    if delay:
        time_ = len(msg) / 50.0
        sleeping(1)

    if smartlander:
        print("smartlander is here")
        print(msg)
        msg = msg.replace('🍮', "༼ ༽")
        print(msg)
    msg = msg.split('\n')
    for line in msg:
        printIRC(":" + botnick + '!' + " PRIVMSG " + chan + " :" + line + '\n')
        try:
            ircsock.send(bytes("PRIVMSG " + chan + " :" + line + "\n", 'UTF-8'))
        except Exception as e:
            logerror(e)
            connected = False


def pm(name, msg):  # This is the send message function, it simply sends messages to the channel.
    global connected
    print("PM'd " + name + ": " + msg)
    try:
        ircsock.send(bytes("PRIVMSG " + name + " :" + msg + "\n", 'UTF-8'))
    except Exception as e:
        logerror(e)
        connected = False


def joinchan(chan):  # This function is used to join channels.
    ircsock.send(bytes("JOIN " + chan + "\n", 'UTF-8'))


def fileprint(chan, stri):
    with open(chan + ".txt", 'a') as f:
        f.write(stri.replace(chan, '').strip().strip('\n') + '\n')
    print(stri)


def printIRC(mess):
    # print(mess)
    timestr = "[" + strftime("%d/%m/%Y %H:%M:%S") + "] "
    mess = mess.strip().strip('\n')
    usr = mess[mess.find(':'):mess.find('!')].strip(':')
    if "NOTICE" in mess:
        print(timestr + "Notice from " + usr + ': ' + mess[mess.find("NOTICE ") + 7:])
        return 0
    if "JOIN" in mess:
        chan = '#' + mess.split('#')[1].split()[0]
        fileprint(chan, timestr + chan + '\t' + usr + " joined " + chan)
        return 0
    if "PART" in mess:
        chan = '#' + mess.split('#')[1].split()[0]
        mess = mess.split('PART')[1]
        mess = mess[mess.find(':') + 1:].strip('\n')
        fileprint(chan, timestr + chan + '\t' + usr + " left " + chan + " (" + mess + ")")
        return 0
    if "QUIT" in mess:
        mess = mess.split('QUIT')[1]
        mess = mess[mess.find(':') + 1:].strip('\n')
        for chan in channel:
            fileprint(chan, timestr + chan + '\t' + usr + " quit " + "(" + mess + ")")
        return 0
    if "MODE" in mess:
        return 0
    if "NICK" in mess:
        mess = mess.split('NICK')[1]
        mess = mess[mess.find(':') + 1:].strip('\n')
        for chan in channel:
            fileprint(chan, timestr + '\t' + '\t' + usr + " is now known as " + mess)
        return 0
    if "CTCP" in mess:
        return 0

    try:
        chan = '#' + mess.split('#')[1].split()[0]
    except Exception:
        chan = "PM"
    try:
        mess = mess.split('PRIVMSG')[1]
    except Exception as e:
        logerror(e)
        return
    mess = mess[mess.find(':') + 1:].strip('\n')
    if "ACTION" in mess:
        fileprint(chan, timestr + chan + '\t' + '*' + usr + mess[1:len(mess) - 1].strip().strip("ACTION"))
    else:
        fileprint(chan, timestr + chan + '\t' + '<' + usr + '>' + '\t' + mess)
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
        timers['space'] = 300


def greet(_channel, mess):
    usr = mess[1:mess.find('!')]
    sendmsg(_channel, "Hey " + usr + "!")
    sendmsg(_channel, "o/")


def rektwiki(_channel, mess):
    if "rekt wiki" in mess:
        mess = mess[mess.find("rekt wiki"):]
        mess = mess.replace("rekt wiki", '')
    mess = mess.strip()
    try:
        r = request.urlopen("http://lt-rekt.wikidot.com/search:site/q/" + mess.strip().replace(' ', '\%20'))
    except Exception as e:
        logerror(e)
        return
    htmlstr = r.read().decode().replace(' ', '').replace('\t', '').replace('\n', '')
    htmlstr = htmlstr[htmlstr.find("<divclass=\"title\"><ahref=\""):].replace("<divclass=\"title\"><ahref=\"", '')
    htmlstr = htmlstr[:htmlstr.find("\""):].replace("\"", '')
    # print(htmlstr + '\n')
    sendmsg(_channel, htmlstr)


def removeTags(mess):
    mess = mess.replace('<span style="text-decoration: underline">', '')
    mess = mess.replace('<span style="font-weight: bold">', '')
    mess = mess.replace('<span style="font-style: italic">', '')
    mess = mess.replace('</span>', '')
    return mess


def splitInLines(mess):
    return mess.replace('<br/>', '\n')


def setrekturl(_channel, mess):
    global rekturl
    newurl = mess[mess.find("update") + 6:].strip('\n').strip()
    f = open('rekt.txt', 'w')
    f.write(newurl)
    rekturl = newurl
    sendmsg(_channel, "Okay, " + newurl + " is saved as the new update! ^.^")


def rektposts(user, channel):
    url = rekturl
    if 'start' not in url:
        url = url.replace('#', '&start=0#')
    nicks = {}
    with open('charnames.txt') as f:
        for line in f:
            line = line.split('&')
            nicks[line[0]] = False
    head = {'User-Agent': 'Chrome/35.0.1916.47'}
    loggedin = False
    if forumusername != "" and forumpw != "":
        lurl = "http://forums.ltheory.com/ucp.php?mode=login"
        payload = {"username": forumusername, \
                   "password": forumpw, \
                   'redirect': 'index.php', \
                   'sid': '', \
                   'login': 'Login'}
        try:
            p = session.post(lurl, headers=head, data=payload, timeout=5)
            loggedin = True
        except Exception as e:
            logerror(e)
            loggedin = False
    htmlstr = ""
    prevhtmlstr = ""
    keepgoing = True
    chars = {}
    while keepgoing:
        if loggedin:
            try:
                r = session.get(url, headers=head, timeout=15)
            except Exception as e:
                logerror(e)
                return
            htmlstr = r.text
        else:
            req = request.Request(url, data=None, headers=head)
            try:
                r = request.urlopen(req, timeout=15)
            except Exception as e:
                logerror(e)
                return
            # print(r.geturl())
            htmlstr = r.read()

        try:
            htmlstr = htmlstr.decode()
        except Exception:
            htmlstr = str(htmlstr)

        # make new url for next attempt
        try:
            startIndicator = int(url[url.find('start=') + 6:url.find('#')])
        except Exception as e:
            sendmsg(channel, "Something went wrong. The update url is probably wrong. Sorry!")
            logerror(e)
        newstart = startIndicator + 15
        url = url.replace('start=' + str(startIndicator), 'start=' + str(newstart))

        # parse html
        parsed_html = BeautifulSoup(htmlstr)

        prev_parsed_html = BeautifulSoup(prevhtmlstr)
        if prevhtmlstr != "":
            if parsed_html.body.find('div', attrs={'class': 'content'}).text == prev_parsed_html.body.find('div',
                                                                                                           attrs={
                                                                                                               'class': 'content'}).text:
                # we reached the end of the thread
                keepgoing = False
                break
            else:
                prevhtmlstr = htmlstr
        else:
            prevhtmlstr = htmlstr
        for i in range(0, 4):
            try:
                parsed_html.blockquote.decompose()
            except Exception:
                pass

        links = [str(tag.find_all('a')[0]) for tag in parsed_html.body.find_all('p', attrs={'class': 'author'})]
        auths = [tag.find_all('a')[1].text for tag in parsed_html.body.find_all('p', attrs={'class': 'author'})]
        posts = parsed_html.body.find_all('div', attrs={'class': 'content'})

        # find actual starting post
        startat = 0
        for i, link in enumerate(links):
            links[i] = link[link.find('"'):link.find('">')].replace(link[link.find('&amp'):link.find('#')], '').strip(
                '"').strip('.')
            if links[i][links[i].find('#'):] == url[url.find('#'):]:
                startat = i
        # cut of unneeded parts of the array
        links = links[startat:]
        auths = auths[startat:]
        posts = posts[startat:]


        # pars posts
        for j, stuff in enumerate(posts):
            # check if char is in
            commanding = False
            for underlined in stuff.find_all('span', attrs={'style': "text-decoration: underline"}):
                underlined = removeTags(str(underlined))
                underlined = splitInLines(underlined)
                underlined = underlined.splitlines()
                for i, line in enumerate(underlined):
                    line = line.replace('\n', '').strip()
                    if line is not "":
                        if line.startswith('"'):
                            commanding = True
                        if commanding:
                            pass
                        else:
                            nicks[auths[j]] = True
                        if line.endswith('"'):
                            commanding = False
    notposted = []
    for key, value in nicks.items():
        if not value:
            notposted.append(key)
    if len(notposted) == 0:
        sendmsg(channel, "Everyone has posted, update time! ^.^")
    elif len(notposted) == 1:
        sendmsg(channel, "Only " + notposted[0] + " hasn't posted yet.")
    else:
        topost = ""
        for i in range(0, len(notposted) - 1):
            topost += notposted[i] + ", "
        topost = topost.strip(', ')
        topost += " and " + notposted[len(notposted) - 1]
        pm(user, topost + " haven't posted yet.")


def findtitle(_channel, mess):
    global session
    print("Finding title")
    res = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                     mess)
    head = {'User-Agent': 'Chrome/35.0.1916.47'}

    if forumusername != "" and forumpw != "":
        url = "http://forums.ltheory.com/ucp.php?mode=login"
        payload = {"username": forumusername, \
                   "password": forumpw, \
                   'redirect': 'index.php', \
                   'sid': '', \
                   'login': 'Login'}
        try:
            p = session.post(url, headers=head, data=payload, timeout=5)
        except Exception as e:
            logerror(e)
            pass
    if "ltheory" in res[0]:
        try:
            r = session.get(res[0], headers=head, timeout=15)
        except Exception as e:
            logerror(e)
            return
        htmlstr = r.text
    else:
        r = requests.head(url=res[0])
        #print(r.headers['content-type'])
        if not r.headers['content-type'].startswith("text"):
            return
        try:
            r = requests.get(res[0], data=None, headers=head, timeout = 15, stream = True)
        except Exception as e:
            logerror(e)
            return
        # print(r.geturl())
        i = 0
        htmlstr = ""
        try:
            for chunk in r.iter_content(chunk_size = 1024):
                htmlstr += chunk.decode()
                if "</title>" in htmlstr:
                    break
                if i>15:
                    break
                i+=1
        except Exception as e:
            logerror(e)
            return
        #print(htmlstr)
    # print(r.geturl())

    try:
        htmlstr = htmlstr.decode()
    except Exception as e:
        htmlstr = str(htmlstr)
    parsed_html = BeautifulSoup(htmlstr)
    try:
        title = parsed_html.title.text
    except Exception as e:
        logerror(e)
        return
    title = title.replace("",'')
    title = title.replace("\n",' ').replace('\r',' ')
    # print(htmlstr)
    # htmlstr=htmlstr.decode().replace('\t','').replace('\n','')
    # print(htmlstr)
    #print(title)
    if len(title)>400:
        title = title[0:400]+"..."
    if htmlstr != "":
        sendmsg(_channel, title)


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
            logerror(e)
            message = "Something went wrong. It's the fault of the python library makers!"
            sendmsg(_channel, message, delay=False)
            return
    buf = io.StringIO(str(message))
    read = buf.readline()
    #print(read)
    testbool = False
    while read != "":
        sendmsg(_channel, read.strip().replace('\n', ''), delay=testbool)
        read = buf.readline()
        testbool = True
    if count != 1:
        sendmsg(_channel, "https://en.wikipedia.org/wiki/" + pageresult.replace(' ', '_'))


def inpsay():
    # cmd = sys.stdin.readline()
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
            queue.insert(0, ":Dinosawer!Dinosawer@Dinosawer.user.gamesurge PRIVMSG " + channel[0] + " :" + cmd)
        else:
            sendmsg(channel[0], cmd)


def stripleft(string, stuff):
    return string[string.find(stuff) + len(stuff):]


def blacklisted(user):
    global blacklist
    return any([stuff in user.lower() for stuff in blacklist])


def logslastn(chan, n):
    mess = ""
    lines = tailer.tail(open(chan + ".txt", errors='ignore'), n)
    for line in lines:
        mess += line + '\n'

    '''url = 'http://pastebin.com/api/api_post.php'
    payload = {"api_option": "paste",\
               "api_dev_key": "ae7566ad9d35a376849f31a49f709bd6",\
               "api_paste_code": mess,\
               "api_paste_expire_date": "1H",\
               "api_paste_private": 0,\
               "api_paste_name": "logs",\
               "api_paste_format": "text",\
               "api_user_key": ''}'''
    url = "http://paste.ee/api"
    payload = {"key": "2f7c3fb1a18609292fb8cc5b8ca9e0bb", \
               "description": "logs" + "[" + strftime("%d/%m/%Y %H:%M:%S") + "]", \
               "paste": mess, \
               "format": "simple"}
    # headers = {'content-type': 'application/json'}
    data = parse.urlencode(payload)
    data = data.encode('utf-8')
    # req = request.Request(url, data, headers)
    response = request.urlopen(url, data,timeout = 10)
    the_page = response.read().decode('utf-8')
    # print(the_page)
    return (the_page)

def getdate(line):
    test = line[line.find('[') + 1:line.find(']')]
    test = test.split(' ')
    test[0] = test[0].split('/')
    test[1] = test[1].split(':')
    day = int(test[0][0])
    month = int(test[0][1])
    year = int(test[0][2])
    hour = int(test[1][0])
    minute = int(test[1][1])
    sec = int(test[1][2])
    ti = datetime.datetime(year, month, day, hour, minute, sec)
    return ti

def logslasth(chan, h):
    mess = ""
    
    amlines = 60*round(h)*5
    if amlines > logmax:
        amlines = logmax
    if amlines < 50:
        amlines = 50
    #print(amlines)
    lines = tailer.tail(open(chan + ".txt", errors='ignore'), amlines)
    n = datetime.datetime.now()
    #for some reason the first element is borked
    del lines[0]
    line = lines[0]
    #for people who ask ridiculous amounts of lines
    ti = getdate(line)
    ti = n - ti
    mess = ""
    if ti.total_seconds() < h * 3600:
        for line in lines:
            mess += line + '\n'
    else:
        lines.reverse()
        for line in lines:
            line = line.strip('\n').strip()
            #print(line)
            if line != '':
                try:
                    ti = getdate(line)
                    ti = n - ti
                    if ti.total_seconds() > round(h * 3600):
                        break
                    else:
                        mess = line + '\n' + mess
                except Exception:
                    pass
    #print("yay")
    url = "http://paste.ee/api"
    payload = {"key": "2f7c3fb1a18609292fb8cc5b8ca9e0bb", \
               "description": "logs" + "[" + strftime("%d/%m/%Y %H:%M:%S") + "]", \
               "paste": mess, \
               "format": "simple"}
    # headers = {'content-type': 'application/json'}
    data = parse.urlencode(payload)
    data = data.encode('utf-8')
    # req = request.Request(url, data, headers)
    #print("sending")
    response = request.urlopen(url, data, timeout = 10)
    the_page = response.read().decode('utf-8')
    #print("yay")
    # print(the_page)
    return (the_page)


def logslastseen(chan, user):
    mess = ""
    lines = tailer.tail(open(chan + ".txt", errors='ignore'), logmax)
    lines.reverse()
    n = datetime.datetime.now()
    try:
        user = user[0:4]
    except Exception:
        pass
    #print(user)
    pinged = False
    for line in lines:
        line = line.strip('\n').strip()
        if line != '':
            #print(line)
            if user in line and "ping timeout" in line.lower() and "quit" in line.lower() and '<' not in line.lower() and '*' not in line.lower():
                pinged = True
            if pinged:
                if "<" + user in line:
                    mess = line + '\n' + mess
                    break
                else:
                    mess = line + '\n' + mess
            else:
                if user in line and ("quit" in line.lower() or "left" in line) and '<' not in line.lower() and '*' not in line.lower():
                    mess = line + '\n' + mess
                    break
                else:
                    mess = line + '\n' + mess
    #print(mess)
    url = "http://paste.ee/api"
    payload = {"key": "2f7c3fb1a18609292fb8cc5b8ca9e0bb", \
               "description": "logs" + "[" + strftime("%d/%m/%Y %H:%M:%S") + "]", \
               "paste": mess, \
               "format": "simple"}
    # headers = {'content-type': 'application/json'}
    data = parse.urlencode(payload)
    data = data.encode('utf-8')
    # req = request.Request(url, data, headers)
    response = request.urlopen(url, data, timeout = 10)
    the_page = response.read().decode('utf-8')
    #print(the_page)
    return (the_page)


def connect():
    global queue
    global ircsock
    global connected
    # Here we connect to the server using the port 6667
    connected = False
    while not connected:
        try:
            print("Trying to connect...")
            ircsock.connect((server, 6667))
            connected = True
        except Exception as e:
            logerror(e)
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
            read = str(buf.readline())
            if read != "":
                read = read.split('\r\n')
                for stuff in read:
                    queue.append(stuff)
            else:
                break
        mess = queue[0]  # removing any unnecessary linebreaks.
        mess = mess.strip().strip('\n\r').strip('\r\n').strip()
        print(mess) # Here we print what's coming from the server
        if mess.find("Found your hostname") != -1 or mess.find("No ident response") != -1:
            sent = "NICK " + botnick + "\n" + "USER " + botnick + " " + botnick + " " + botnick + " :This is a result of a tutoral covered on http://shellium.org/wiki.\n"
            ircsock.send(bytes(sent, 'UTF-8'))  # here we actually assign the nick to the bot
            print(sent)
        if mess.find("Welcome to the GameSurge IRC") != -1:  # if the server pings us then we've got to respond!
            break
        if "PING" in mess or "PONG" in mess:  # if the server pings us then we've got to respond!
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
        _channel, user, mess = printIRC(mess)
    except Exception as e:
        # some weird message?
        #print(mess)
        f = open('error.txt')
        try:
            f.write(str(mess) + '\n')
        except Exception:
            pass
        f.close()
        logerror(e)
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
        if not blacklisted(user):
            if "saoirse" in lmess:
                if any([greeting in lmess for greeting in greetings]):
                    sendmsg(_channel, random.choice(greetings).title() + "!")
                    # lmess=stripleft(lmess,"saoirse")
                # mess=stripleft(mess,"Saoirse")
                # print(lmess)
                if "Dinosawer" in user:
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
                        sendmsg(_channel, "Nope!")
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
                        return
                    elif "ignore" in lmess and "Dinosawer" in user:
                        nick = lmess[lmess.find("ignore") + len("ignore"):].strip()
                        if nick != "dinosawer":
                            blacklist.append(nick)
                            writeblacklist()
                            return
                if "rekt" in lmess and "post" in lmess:
                    rektposts(user, _channel)
                    return
                if "set rekt update" in lmess:
                    setrekturl(_channel, lmess)
                    return
                if "shush" in lmess:
                    sendmsg(_channel, "OK, I'll shut up :(")
                    shushed = True
                    timers['shushed'] = 1800
                    return
                elif "speak" in lmess:
                    sendmsg(_channel, "Yay! Pudding!")
                    shushed = False
                    timers['shushed'] = 0
                    return
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
            if "!logs" in lmess:
                try:
                    n = lmess[lmess.find("!logs"):].strip().split(' ')[1].strip()
                    if n.endswith('h'):
                        try:
                            n = n.replace('h', '')
                            n = float(n)
                            if n<0:
                                raise ValueError('negative value')
                        except Exception:
                            sendmsg(_channel, "Please enter a valid number of lines to paste! ^.^")
                            return
                        sendmsg(_channel, logslasth(_channel, n))
                        return
                    elif n.endswith('m'):
                        try:
                            n = n.replace('m', '')
                            n = float(n) / 60
                            if n<0:
                                raise ValueError('negative value')
                        except Exception:
                            sendmsg(_channel, "Please enter a valid number of lines to paste! ^.^")
                            return
                        sendmsg(_channel, logslasth(_channel, n))
                        return
                    else:
                        try:
                            n = int(n)
                            if n<0:
                                raise ValueError('negative value')
                        except Exception:
                            sendmsg(_channel, "Please enter a valid number of lines to paste! ^.^")
                            return
                        if n > logmax:
                            sendmsg(_channel, "Sorry, won't do more than " + str(logmax) + " ^.^")
                            n = logmax
                        sendmsg(_channel, logslastn(_channel, n))
                        return
                except Exception as e:
                    sendmsg(_channel, "Something went wrong. Tell Dinosawer: "+str(e)+'"')
                    logerror(e)
                    return
                    

            if "!loglast" in lmess:
                sendmsg(_channel, logslastseen(_channel, user))
                return
            if "rekt wiki" in lmess:
                rektwiki(_channel, lmess)
                return
            if "[[[" in lmess:
                try:
                    rektwiki(_channel, lmess[lmess.find('[[['):lmess.find(']]]')].replace('[', '').replace(']', ''))
                except Exception as e:
                    logerror(e)
                    return
            if "http://www.gamesurge.net/cms/spamServ" not in lmess and len(
                    re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                               lmess)) != 0:
                findtitle(_channel, mess)
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
            if not shushed and re.search(regex1, lmess) is not None:
                sendmsg(_channel, "DOOOOMED!")
                return
            if not shushed and re.search(regex2, lmess) is not None:
                space(_channel)
                return
            if "!procemo" in lmess:
                procemo(_channel)
                return
            if "!listemo" in lmess or "!emoticonlist" in lmess:
                listemo(_channel, user, mess)
                return


        if not shushed:
            for key, value in triggers.items():
                if any([stuff in lmess for stuff in key]):
                    if timers[key[0]] <= 0 and (not blacklisted(user) or bottriggers[key[0]]):
                        sleeping(0.6)
                        sendmsg(_channel, value)
                        timers[key[0]] = timervals[key[0]]
                        return
    return


def main():
    global ircsock
    global timers
    global shushed
    # ircsock.setblocking(0)
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
        if timers['shushed'] == 0:
            shushed = False
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