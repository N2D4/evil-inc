from __future__ import division
import discord
import pickle
import os
import re
import random
import asyncio
import math
import json

markov_channels = {}

start_sym = '\t'
end_sym = '\n'
markov = {
    (start_sym,): ['ok'],
    (start_sym, start_sym): ['ok'],
    ('ok',): [end_sym],
    (start_sym, 'ok'): [end_sym]
}

cur_updating = False

markovid = None

totalMatches = 0

def set_follow_id(id):
    global markovid
    markovid = id

async def on_markov_message(client: discord.Client, message: discord.Message):
    raise Exception("Unimplemented!")

async def update_markovs(client: discord.Client, channel: discord.TextChannel, created_at, yielddist = 1000, yieldlog = 1.5):
    global cur_updating
    while (cur_updating):
        print("Currently updating. Back to sleep for a second...")
        await asyncio.sleep(1)
    try:
        cur_updating = True
        global markovid
        nextyield = yielddist
        i = 0
        j = 0
        limit = 25
        before = None
        f = True
        sc = gsc(channel)
        after = sc.last_checked
        while (f or before != None):
            f = False
            bb = before
            before = None
            async for message in channel.history(limit=limit, before=bb):
                if after != None and message.created_at <= after:
                    continue
                if (before == None or message.created_at < before) and (bb == None or message.created_at < bb):           # maybe fix: if messages were sent in the same time frame, it won't correctly read them
                    before = message.created_at
                if add_message(message):
                    j += 1
                i += 1
                limit += 1
                if i >= nextyield:
                    print("Checked " + str(i) + " messages in channel " + channel.name + " (found " + str(j) + ")")
                    yield i
                    nextyield *= 1 + yieldlog

        print("Markov check done! Checked " + str(i) + " messages in channel " + channel.name + " (found " + str(j) + ")")
        yield i
    finally:
        cur_updating = False


def add_message(message: discord.Message):
    sc = gsc(message.channel)
    return sc.add_message(message)


def gsc(channel: discord.TextChannel):
    global markov_channels
    sc = markov_channels.get(channel.id, None)
    if sc == None:
        sc = markov_channel()
    markov_channels[channel.id] = sc
    return sc

def save():
    global markov_channels
    print("Saving Markov!")
    with open('markov_channels', 'wb') as fp:
        pickle.dump(markov_channels, fp)

def load():
    global markov_channels, markov
    print("Saving Markov!")
    if (os.path.isfile('markov_channels')):
        with open('markov_channels', 'rb') as fp:
            markov_channels = pickle.load(fp)
        print("Reloading Markov...")
        old_markov = markov
        markov_reset()
        for channel in markov_channels.values():
            for message in channel.messages:
                markov_add_message(message)
        print("Reloaded Markov!")
        print("Unique Markov terms: " + str(len(markov)))
        if len(markov) == 0:
            print("That means it's empty! Resetting Markov to previous state...")
            markov = old_markov
        else:
            print("Starting terms: " + str(len(markov[stemmer(start_sym)])))
    else:
        print("File not found! Resetting markov_channels")
        markov_channels = {}

def deleteFile():
    os.remove('markov_channels')
    load()
    

def get_char_count():
    global markov_channels
    result = 0
    for _, markov_channel in markov_channels.items():
        for message in markov_channel.messages:
            result += len(message)
    return result

def json_dump():
    print("Dumping JSON to markov_channels_out.json")
    with open('markov_channels_out.json', 'w') as fp:
        json.dump({a: b.messages for a, b in markov_channels.items()}, fp)

def stemmer(msg1, msg2=None):
    global start_sym, end_sym
    def stem(msg):
        return msg if msg == start_sym or msg == end_sym else re.sub(r'[.!?:;\-/\'\(\)\[\]\{\}]', '', msg)
    return (stem(msg1),) if msg2 == None else (stem(msg1), stem(msg2))

def markov_reset():
    global markov
    markov = {}

def markov_add_message(msg: str):
    global start_sym, end_sym, markov
    syms = [start_sym, *[x for x in msg.split() if stemmer(x) != ""], end_sym]
    if len(syms) <= 3:
        return
    lsym = start_sym
    sym = start_sym
    for i in range(len(syms)):
        allof = [stemmer(sym), stemmer(lsym, sym)]
        for a in allof:
            if a not in markov:
                markov[a] = []
            markov[a].append(syms[i])
        lsym = sym
        sym = syms[i]

def markov_generate():
    global start_sym, end_sym, markov
    msg = []
    lsym = start_sym
    sym = start_sym
    while len(msg) < 100:
        arr1 = markov[stemmer(sym)]
        arr2 = markov[stemmer(lsym,sym)]
        arr = arr2 if random.random() >= 1.0 / math.sqrt(1 + len(arr2)) else arr1
        new_sym = arr[random.randint(0, len(arr)-1)]
        if new_sym == end_sym:
            break
        msg.append(new_sym)
        lsym = sym
        sym = new_sym
    return ' '.join(msg)



class markov_channel:
    def __init__(self):
        self.last_checked = None
        self.messages = []

    def add_message(self, message: discord.Message):
        global totalMatches
        if self.last_checked == None or message.created_at > self.last_checked:
            self.last_checked = message.created_at
        if (message.author.id == markovid):
            msg = str(message.content)
            markov_add_message(msg)
            self.messages.append(msg)
            prog = re.compile('^s[^ ]*t\s|^s[^ ]*t$|\ss[^ ]*t$|\ss[^ ]*t\s|UL|olo|lol|ele|lel|hah|aha|ek')
            match = prog.findall(message.content)
            if len(match) != 0:
                totalMatches += len(match)
            return True
        return False
