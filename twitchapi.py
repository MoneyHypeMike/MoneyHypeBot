import urllib.request
import json
import re

def twitch_channel(channel):
    link = "https://api.twitch.tv/kraken/channels/" + channel[1:]
    content = urllib.request.urlopen(link)
    data = json.loads(content.read().decode("utf-8"))
    return data['status']