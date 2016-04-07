import socket
import io


# from time import sleep


class Server:
    def __init__(self, server, channels, name, nick):
        self.server = server
        self.channels = channels
        self.name = name
        self.connected = False
        self.queue = []
        self.connect(nick)

    def connect(self, nick):
        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Here we connect to the server using the port 6667
        self.connected = False
        while not self.connected:
            try:
                self.ircsock.connect((self.server, 6667))
                self.connected = True
            except Exception:
                self.connected = False
                return self.connected
                # sleeping(5)
        self.ircsock.settimeout(180)
        self.ircsock.send(bytes(
            "USER " + nick + " " + nick + " " + nick + " :This is a result of a tutorial covered on http://shellium.org/wiki.\n",
            'UTF-8'))  # user authentication
        self.ircsock.send(bytes("NICK " + nick + "\n", 'UTF-8'))  # here we actually assign the nick to the bot
        while 1:  # Be careful with these! it might send you to an infinite loop
            ircmsg = self.ircsock.recv(2048)  # receive data from the server
            buf = io.StringIO(str(ircmsg))
            while True:
                read = buf.readline()
                if read != "":
                    self.queue.append(read)
                else:
                    break
            mess = self.queue[0]  # removing any unnecessary linebreaks.
            mess = mess.strip('\n\r').strip()
            # print(mess) # Here we print what's coming from the server
            if mess.find("Found your hostname") != -1 or mess.find("No ident response") != -1:
                sent = "NICK " + nick + "\n" + "USER " + nick + " " + nick + " " + nick + " :This is a result of a tutoral covered on http://shellium.org/wiki.\n"
                self.ircsock.send(bytes(sent, 'UTF-8'))  # here we actually assign the nick to the bot
                print(sent)
            if mess.find("Welcome to the GameSurge IRC") != -1:  # if the server pings us then we've got to respond!
                break
            if mess.find("PING :") != -1:  # if the server pings us then we've got to respond!
                ping(mess)
            if len(self.queue) != 0:
                del self.queue[0]
        # Join the channel using the functions we previously defined
        '''if auth:
            pm("AuthServ@Services.GameSurge.net", "AUTH " + username + " " + password)'''
        for chan in self.channels:
            self.joinchan(chan)
        self.queue = []
        return self.connected

    def sendmsg(self, chan, msg):  # This is the send message function, it simply sends messages to the channel.
        msg = msg.split('\n')
        for line in msg:
            self.ircsock.send(bytes("PRIVMSG " + chan + " :" + line + "\n", 'UTF-8'))

    def pm(self, name, msg):  # This is the send message function, it simply sends messages to the channel.
        msg = msg.split('\n')
        for line in msg:
            ircsock.send(bytes("PRIVMSG " + name + " :" + line + "\n", 'UTF-8'))

    def joinchan(self, chan):  # This function is used to join channels.
        if chan not in self.channels:
            self.channels.append(chan)
        self.ircsock.send(bytes("JOIN " + chan + "\n", 'UTF-8'))

    def ping(self, mess):  # This is our first function! It will respond to server Pings.
        self.ircsock.send(bytes('PONG %s\r\n' % mess, 'UTF-8'))

    def receive(self):
