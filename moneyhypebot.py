# Import necessary modules to run the IRC bot
import socket
import re
import threading
import random
import time
import formulas
import speciedex
import worldrecords
import twitchapi

# Information to connect to twitch IRC server
SERVER = "irc.twitch.tv"
PORT = 6667

# Information to authenticate to twitch IRC server
NICK = "moneyhypebot"
PASS = "oauth:76sps7rc65egy7e8lgneq6ohs9cu5iz"
CHANNEL = "#moneyhypemike"

# Information to treat data from twitch IRC server
BUFFSIZE = 1024

#Used for emotes
counter = 0
timer = 0
timer2 = 0
names = []

channels = {CHANNEL}

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

def globalprotection():
    """Protects against global ban"""
    
    global queue
    queue = 0
    threading.Timer(30, globalprotection).start()

def output(msg, chan):
    """Outputs a message in twitch chat"""
    
    global queue
    queue += 1
    
    if queue < 20:
        irc.send(("PRIVMSG {} :{}\r\n".format(chan, msg)).encode())
        print("{}: {}".format(chan, msg))

def join(chan):
    """Joins a channel"""
    
    global channels
    temp = "#{}".format(chan[6:])
    irc.send(("JOIN {}\r\n".format(temp).encode()))
    channels.add(temp)
    print("Joined {}\nCurrently in the following channels: {}".format(temp, channels))

def quit(chan):
    """Leaves a channel"""
    
    global channels
    temp = "#" + chan[6:]
    irc.send(("PART {}\r\n".format(temp)).encode())
    channels.remove(temp)
    print("Left {}\nCurrently in the following channels: {}".format(temp, channels))

def spin(num=3):
    """Returns a slot combination"""
    
    num = num.split()[1]
    emotes = ["FrankerZ", "KevinTurtle", "PogChamp", "OpieOP", "Kreygasm", 
              "MVGame", "Jebaited", "Kappa", "PJSalt"]
    
    try:
        num = int(num) 
        if num > 5: num = 5
        slot = [random.choice(emotes) for x in range(num)]
        
        return "|".join(slot)
    except ValueError:
        return "Could not convert '{}' to an integer.".format(num)

def globalemote():
    """Outputs a random emote in Werster channel"""
    
    global channels
    if "#werster" in channels:
        emotes = ["KevinTurtle", "KevinSquirtle", "WooperZ"]
        output(random.choice(emotes), "#werster")
    
    threading.Timer(180, globalemote).start()

def stat2int(stat_name):
    """Returns the integer value of the stat"""
    names = ["hp", "atk", "def", "spa", "spd", "spe"]
    
    try:
        return names.index(stat_name)
    except ValueError:
        return "Invalid stat name (expected hp/atk/def/spa/spd/spe, "\
               "received '{}').".format(stat_name)

def dv(message):
    """Returns the possible DV of a pokemon"""
    info = [x for x in message.split(maxsplit=6)[1:]]
    num_info = len(info)
    stat_exp = info[5] if num_info == 6 else 0
    
    if (5 <= num_info <= 6):
        try:
            gen = int(info[0])
            name = info[1].upper()
            stat_name = stat2int(info[2])
            level = int(info[3])
            stat_value = int(info[4])
            
            if num_info == 6:
                stat_exp = int(info[5])
        except ValueError:
            return "Could not convert one of the following string to an "\
                   "integer: '{}' (gen), '{}' (level), '{}' (stat) and '{}' "\
                   "(stat exp).".format(info[0], info[3], info[4], stat_exp)
        else:
            if gen < 0 or gen > 5:
                return "Invalid generation value (expected 1 or 2, received "\
                       "'{}')".format(gen)
            
            if type(stat_name) == str:
                return stat_name
            
            if level < 0 or level > 100:
                return "Invalid level value (expected 1-100, received '{}')."\
                       .format(level)
            
            if stat_value < 0 or stat_value > 255:
                return "Invalid stat value (expected 1-255, received '{}'.)"\
                       .format(stat_value)
            
            if stat_exp < 0 or stat_exp > 65536:
                return "Invalid stat exp value (expected 1-65536, received "\
                       "'{}'.)".format(stat_exp)
            
            try:
                specie = speciedex.all.dex[gen][name]
                return formulas.calc_dv(gen, specie.base_stats[stat_name], 
                                        level, stat_value, stat_exp)
            except KeyError:
                return "Invalid pokémon specie for selected generation "\
                           "(expected a valid pokémon specie, received '{}')."\
                           .format(name)
    else:
        return "Syntax: $dv gen_num pkmn_name stat_name level stat_value "\
               "base_exp (base_exp is optional and defaults to 0)"

def wr(message):
    """Returns the world record for the specified game and category"""
    info = [x for x in message.split(maxsplit=2)[1:]]
    num_info = len(info)
    
    if num_info > 0:
        if info[0] not in worldrecords.games.keys():
            return "Invalid game name (expected '{}', received '{}'"\
                   .format("/".join(worldrecords.games.keys()), info[0])
    
        game_name = info[0]
    
        if num_info == 2:
            category = info[1]
            
            if category not in worldrecords.games[game_name].keys():
                return "Invalid category name (expected '{}', received '{}')."\
                       .format("/".join(worldrecords.games[game_name].keys()),
                               category)
            
            timer2 = time.time()
            return worldrecords.games[game_name][category]
        elif num_info == 1:
            return " ".join(worldrecords.games[game_name].values())
        else:
            return "Syntax: $wr game_abbr category (category is optional and "\
                   "defaults to all possible categories for the selected game"
    else:
        return "Syntax: $wr games_abrv category"
    
def dex(message):
    """Returns a paragraph describing the specie"""
    info = [x for x in message.split(maxsplit=2)[1:]]
    num_info = len(info)
    
    if num_info == 2:
        gen = info[0]
        specie = info[1].upper()
        try:
            gen = int(gen)
            if gen > 0 and gen < 6:
                try:
                    return str(speciedex.all.dex[gen][specie])
                except KeyError:
                    return "Invalid pokémon specie for the selected "\
                           "generation (expected a valid pokémon specie, "\
                           "received '{}').".format(specie)
            else:
                return "Invalid generation number (expected an integer value "\
                       "between 1 and 5, received '{}').".format(gen)
        except ValueError:
            return "Could not convert '{}' to an integer.".format(gen)
    else:
        return "Syntax: $dex gen_num specie_name"

def exp(message):
    """Returns the number of exp gained when the pokemon is defeated"""
    info = [x for x in message.split(maxsplit=5)[1:]]
    num_info = len(info)
    
    if num_info == 3:
        gen = info[0]
        specie = info[1].upper()
        level = info[2]
        try:
            gen = int(gen)
            level = int(level)
            #wild = True if info[3] == "True" else False
            if gen < 6:
                try:
                    total_exp = speciedex.all.dex[gen][specie].base_exp
                    return formulas.calc_exp(gen, level, total_exp)
                except KeyError:
                    return "Invalid pokémon specie for selected generation "\
                           "(expected a valid pokémon specie, received '{}')."\
                           .format(specie)
            else:
                return "Invalid generation number (expected an integer value "\
                       "between 1 and 5, received '{}').".format(gen)
        except ValueError:
            return "Could not convert one of the following string to an "\
                   "integer: '{}' (gen) and '{}' (level))".format(gen, level)
            
def update_channel(channel):
    channels[channel] = twitchapi.twitch_channel(channel)
            
# Initialization of the bot
globalprotection()
#globalemote()

def timeout(nick, chan, time):
    output(".timeout {} {}".format(nick, time), chan)

join("      werster")
join("      eekcast")
    
# Infinite loop to run the bot
while True:
    a = irc.recv(BUFFSIZE).decode(errors="ignore").split("\r\n")
    
    for line in a:
        input = line.split(":",2)
        inputnum = len(input)
        
        if inputnum == 2 and "PING" in input[0]:
            irc.send(("PONG :tmi.twitch.tv\r\n").encode())
        elif inputnum == 3 and "PRIVMSG" in input[1] and "HISTORYEND" not in input[2]:
            inputnick = input[1].split("!")[0]
            inputchan = input[1].split(" ")[2]
            inputmsg = input[2]
            
            if inputmsg.lower().startswith("$dv"):
                output(dv(inputmsg), inputchan)
            elif inputmsg.lower().startswith("$wr") and (time.time() - timer2) > 60:
                output(wr(inputmsg.lower()), inputchan)
                timer2 = time.time()
            elif inputmsg.lower().startswith("$dex") and inputchan != "#werster":
                output(dex(inputmsg), inputchan)
            elif re.search(r"ebola|shibez|b [o0] [iy] [sz]|erino|t[o]* much water|\bign\b", inputmsg,re.I) and inputchan == "#werster":
                if inputnick not in names:
                    names.append(inputnick)
                    timeout(inputnick, inputchan, 1)
                else:
                    n = names.count(inputnick)
                    names.append(inputnick)
                    timeout(inputnick, inputchan, n * 60)
            elif inputmsg.lower().startswith("$exp"):
                output(exp(inputmsg), inputchan)
            elif inputmsg.lower().startswith("$join") and inputnick == "moneyhypemike":
                join(inputmsg)
            elif inputmsg.lower().startswith("$quit") and inputnick == "moneyhypemike":
                quit(inputmsg)
            elif inputmsg.lower().startswith("$spin"):
                output(spin(inputmsg), inputchan)
            elif inputmsg.lower().startswith("$uptime") and inputnick == "moneyhypemike":
                hour = random.randint(0, 12)
                minute = random.randint(0, 59)
                if minute < 10:
                    minute = "0" + str(minute) 
                second = random.randint(0, 59)
                if second < 10:
                    second = "0" + str(second) 
                output("{}:{}:{}".format(hour, minute, second), inputchan)
            #elif inputmsg.lower().startswith("$roulette") and inputnick != "moneyhypemike":
            #    timeout(inputnick, inputchan, random.randint(1, 600))
                
            if inputchan == "#werster":                       
                if "faq" in inputmsg.lower() and (time.time() - timer) > 60 and "http://pastebin.com/NbsprMzM" not in inputmsg and inputnick != "moneyhypebot":
                    output("Please read the FAQ before asking questions: http://pastebin.com/NbsprMzM", inputchan)
                    #http://pastebin.com/kiyRcY3x
                    #http://pastebin.com/AX5EGTfF
                    #http://pastebin.com/S01Syiz0
                    #http://pastebin.com/Jj7i7zke
                    #http://pastebin.com/PMfUdQQ7
                    #http://pastebin.com/6n51JiK8
                    #http://pastebin.com/eRn2su60
                    #http://pastebin.com/NbsprMzM
                    timer = time.time()

                if "KevinTurtle" in inputmsg or "KevinSquirtle" in inputmsg or "WooperZ" in inputmsg or "TopPika" in inputmsg:
                    counter += 1
                    if counter > 20:
                        counter = 0
                        emotes = ["KevinTurtle", "KevinSquirtle", "WooperZ", "TopPika"]
                        output(random.choice(emotes), inputchan)
            elif inputchan == "#eekcast":
                if "KevinTurtle" in inputmsg or "Jebaited" in inputmsg:
                    counter += 1
                    if counter > 20:
                        counter = 0
                        emotes = ["KevinTurtle", "Jebaited"]
                        output(random.choice(emotes), inputchan)
                        
                if "faq" in inputmsg.lower() and (time.time() - timer) > 60 and "http://pastebin.com/4GARS4N6" not in inputmsg and inputnick != "moneyhypebot":
                    output("FAQ: http://pastebin.com/4GARS4N6", inputchan)
                    #http://bombch.us/mPW
                    #http://pastebin.com/4GARS4N6
                    timer = time.time()
            elif inputchan == "#moneyhypemike":
                if "faq" in inputmsg.lower() and (time.time() - timer) > 60 and "http://goo.gl/Qtbn7D" not in inputmsg and inputnick != "moneyhypebot":
                    output("FAQ: http://goo.gl/Qtbn7D", inputchan)
                    #http://goo.gl/Le2x9r
                    #http://goo.gl/W2tE0c
                    #http://goo.gl/Qtbn7D
                    timer = time.time()