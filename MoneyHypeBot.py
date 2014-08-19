# Import necessary modules to run the IRC bot
import socket
import string
import threading
import random
import time
import re
import pkmnformula
import pkmndict
import species

# Information to connect to twitch IRC server
SERVER = "irc.twitch.tv"
PORT = 6667

# Information to authenticate to twitch IRC server
NICK = "moneyhypebot"
PASS = "oauth:9w919ckrf5p1mweytkh1w7n4sl8tzjt"
CHANNEL = "#moneyhypemike"
# Information to treat data from twitch IRC server
BUFFSIZE = 1024
counter = 0
timer = 0

# Connects to twitch IRC server
print("Creating connection to twitch IRC server ...")
irc = socket.create_connection((SERVER, PORT))

# Authenticates to twitch IRC server
print("Sending login information to twitch IRC server ...")
irc.send(("PASS %s\r\n" % PASS).encode())
irc.send(("NICK %s\r\n" % NICK).encode())
irc.send(("USER %s %s %s :%s\r\n" % (NICK, NICK, NICK, NICK)).encode())
irc.send(("JOIN %s\r\n" % CHANNEL).encode())
print("Connection successful !")

# Global ban protection
def globalprotection():
    global queue
    queue = 0
    threading.Timer(30, globalprotection).start()

# Sends message to twitch IRC server
def output(msg, chan):
    global queue
    queue += 1
    
    if queue < 20:
        irc.send(("PRIVMSG %s :%s\r\n" % (chan, msg)).encode())
        print("PRIVMSG %s :%s\r\n" % (chan, msg))
        
# Joins an irc channel
def join(channel, nick):
    if "moneyhypemike" in nick:
        temp = "#" + channel[6:]
        irc.send(("JOIN %s\r\n" % temp).encode())
        print("Joining %s" % temp)

# Quits an irc channel
def quit(channel, nick):
    if "moneyhypemike" in nick:
        temp = "#" + channel[6:]
        irc.send(("PART %s\r\n" % temp).encode())
        print("Quitting %s" % temp)

def spin(channel, n=3):
    emotes = ["FrankerZ", "KevinTurtle", "PogChamp", "OpieOP", "Kreygasm", 
              "MVGame", "Jebaited", "Kappa", "PJSalt"]
    n = int(n.split()[1])
    slot = ""
    if n > 5:
        n = 5
    for i in range(n):
        if i == n - 1:
            slot += random.choice(emotes)
        else:
            slot += random.choice(emotes) + "|"
    output(slot, channel)
    
def globalemote():
    emotes = ["KevinTurtle", "KevinSquirtle", "WooperZ"]
    output(random.choice(emotes), "#werster")
    threading.Timer(180, globalemote).start()

def convert2int(x):
    try:
        n = int(x)
        return abs(n)
    except ValueError:
        return "-1"

def dv(message):
    str_msg = [x for x in message.split(maxsplit=5)[1:]]
    len_msg = len(str_msg)
    
    if (4 <= len_msg <= 5):
        if str_msg[0] not in pkmndict.pkmn.keys():
            return "Invalid Pokémon name (expected nidoran/totodile/mudkip family, received '{}'".format(str_msg[0])
        
        if str_msg[1] not in pkmndict.pkmn[str_msg[0]].keys():
            return "Invalid stat name (expected hp/atk/def/spa/spd/spe, received '{})'".format(str_msg[1])
        
        num_msg = [convert2int(x) for x in str_msg[2:] if convert2int(x) != "-1"]
        if "-1" in num_msg:
            return "Could not convert string value '{}' to integer.".format([x for x in str_msg[2:] if convert2int(x) == "-1"])
        else:
            return pkmnformula.calculate_dv(str_msg[1], pkmndict.pkmn[str_msg[0]][str_msg[1]], *num_msg)
    else:
        return "Invalid number of arguments (expected 4 or 5 arguments, received '{}').".format(len_msg)

def wr(message):
    str_msg = [x for x in message.split(maxsplit=2)[1:]]
    len_msg = len(str_msg)
    
    if str_msg[0] not in pkmndict.wr.keys():
        return "Invalid game name (expected '{}', received '{}'".format("/".join(pkmndict.wr.keys()), str_msg[0])
    
    if len_msg == 2:
        if str_msg[1] not in pkmndict.wr[str_msg[0]].keys():
            return "Invalid category name (expected '{}', received '{}').".format("/".join(pkmndict.wr[str_msg[0]].keys()), str_msg[1])
        
        return pkmndict.wr[str_msg[0]][str_msg[1]]
    elif len_msg == 1:
        return pkmndict.wr[str_msg[0]]
        
    else:
        return "Invalid number of arguments (expected 2 arguments, received '{}').".format(len_msg)

def dex(message):
    str_msg = [x for x in message.split(maxsplit=2)[1:]]
    len_msg = len(str_msg)
    
    if len_msg == 2:
        gen = str_msg[0]
        specie = str_msg[1].capitalize()
        try:
            gen = int(gen)
            if 2 < gen < 6:
                try:
                    return str(species.dex[gen][specie])
                except KeyError:
                    return "Invalid pokémon specie (expected a valid pokémon specie, received '{}').".format(specie)
            else:
                return "Invalid generation number (expected an integer value between 3 and 5, received '{}').".format(gen)
        except ValueError:
            return "'{}' is not an integer.)".format(gen)
    else:
        return "Invalid number of arguments (expected 2 arguments, received {}).".format(len_msg)
    
# Initialization of the bot
globalprotection()
#globalemote()

# Infinite loop to run the bot
while True:
    a = irc.recv(BUFFSIZE).decode().split("\r\n")
    
    for line in a:
        input = line.split(":",2)
        inputnum = len(input)
        
        if inputnum == 2 and "PING" in input[0]:
            irc.send(("PONG :tmi.twitch.tv\r\n").encode())
        elif inputnum == 3 and "PRIVMSG" in input[1] and "HISTORYEND" not in input[2]:
            inputnick = input[1].split("!")[0]
            inputchan = input[1].split(" ")[2]
            inputmsg = input[2]
            
            if inputmsg.startswith("$dv"):
                output(dv(inputmsg.lower()), inputchan)
            elif inputmsg.startswith("$wr"):
                output(wr(inputmsg.lower()), inputchan)
            elif inputmsg.startswith("$dex"):
                output(dex(inputmsg), inputchan)
            elif inputmsg.startswith("$join"):
                join(inputmsg, inputnick)
            elif inputmsg.startswith("$quit"):
                quit(inputmsg, inputnick)
            elif inputmsg.startswith("$spin"):
                spin(inputchan, inputmsg)                
            
            if inputchan == "#werster":                       
                if "faq" in inputmsg.lower() and (time.time() - timer) > 60 and "http://pastebin.com/kiyRcY3x" not in inputmsg and inputnick != "moneyhypebot":
                    output("FAQ: http://pastebin.com/kiyRcY3x", inputchan)
                    #http://pastebin.com/kiyRcY3x
                    #http://pastebin.com/AX5EGTfF
                    #http://pastebin.com/S01Syiz0
                    timer = time.time()
                    
                if "KevinTurtle" in inputmsg or "KevinSquirtle" in inputmsg or "WooperZ" in inputmsg:
                    counter += 1
                    if counter > 20:
                        counter = 0
                        emotes = ["KevinTurtle", "KevinSquirtle", "WooperZ"]
                        output(random.choice(emotes), inputchan)
            elif inputchan == "#eekcast":
                if "KevinTurtle" in inputmsg or "Jebaited" in inputmsg:
                    counter += 1
                    if counter > 20:
                        counter = 0
                        emotes = ["KevinTurtle", "Jebaited"]
                        output(random.choice(emotes), inputchan)
                        
                if "faq" in inputmsg.lower() and (time.time() - timer) > 60 and "http://bombch.us/mPW" not in inputmsg and inputnick != "moneyhypebot":
                    output("FAQ: http://bombch.us/mPW", inputchan)
                    #http://bombch.us/mPW
                    #http://pastebin.com/4GARS4N6
                    timer = time.time()
                    
            elif inputchan == "#moneyhypemike":
                if "faq" in inputmsg.lower() and (time.time() - timer) > 60 and "http://goo.gl/Le2x9r" not in inputmsg and inputnick != "moneyhypebot":
                    output("FAQ: http://goo.gl/Le2x9r", inputchan)
                    timer = time.time()

            elif inputchan == "#vincento341":
                if "faq" in inputmsg.lower() and (time.time() - timer) > 60 and "http://pastebin.com/m7ej5DVS" not in inputmsg and inputnick != "moneyhypebot":
                    output("FAQ: http://pastebin.com/m7ej5DVS", inputchan)
                    timer = time.time()