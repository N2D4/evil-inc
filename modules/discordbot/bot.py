import discord
import asyncio
import markov
import sys
import os
import time
import re
import random
import datetime

with open('config.txt', 'r') as configfile:
    config = configfile.read()

configDelim = "\n========\n"
quotes = config.split(configDelim)[0].splitlines()
token = config.split(configDelim)[1]
adminid = int(config.split(configDelim)[2])
markovid = int(config.split(configDelim)[3])
markov.set_follow_id(markovid)
def save_config():
    with open('config.txt', 'w') as configfile:
        configfile.write(configDelim.join(["\n".join(quotes), token, str(adminid), str(markovid)]))

tellme = ""
maxmsglen = 2000


dabot2letsdo = "nice come wet lit "
dabot2emoteresp = u"\U0001F629"


print("Launching bot...")

client = discord.Client()

@client.event
async def on_ready():
    print('Connected as')
    print(client.user.name)
    print(client.user.id)
    print('------')



def is_spam_msg(s: str):
    return ("repeat" in s or "spam this" in s) and not s.startswith("tell me that")

async def send_spam(s: str, channel: discord.TextChannel):
    if (len(s) + len(tellme) > maxmsglen):
        await channel.send("Message too long!")
        return

    await channel.send(tellme + s)


@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if is_spam_msg(reaction.message.content) and reaction.message.content.startswith(dabot2letsdo) and str(reaction.emoji) == dabot2emoteresp:
        await send_spam(reaction.message.content, reaction.message.channel)


@client.event
async def on_message(message: discord.Message):
    try:
        if (message.author == client.user):
            return

        #print("Received message from user: " + str(message.author) + ": " + message.content)

        
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
        
        for attachment in message.attachments:
            urls.append(attachment.url)
        
                    
        
        if message.author.id == markovid:
            await markov.on_markov_message(client, message)
        
        
        if is_spam_msg(message.content) and not message.content.startswith(dabot2letsdo):
            global tellme
            s = dabot2letsdo + message.content
            await send_spam(s, message.channel)
            
        if message.content == "how much spam" and message.author.id == adminid:
            count = markov.get_char_count()
            await(message.channel.send("The target has written " + str(count) + " characters!"))
            
        elif message.content == "!stop" and message.author.id == adminid:
            print("Stopping!")
            await(message.channel.send("Stopping now!"))
            stop_bot()
            
        elif message.content == "!restart" and message.author.id == adminid:
            await message.channel.send("Restarting is currently disabled. Please use !stop; the bot is set up to restart on crash")
            # print("Restarting!")
            # await(message.channel.send("Restarting now!"))
            # restart_bot()

        elif message.content == "!update" and message.author.id == adminid:
            await message.channel.send("Updating Markov...")
            steps = markov.update_markovs(client, message.channel, message.created_at, yielddist=1000, yieldlog=1.1)
            async for i in steps:
                await message.channel.send("Checked " + str(i) + " messages from this channel!")
            
            await message.channel.send("Saving...")
            markov.save()
            
            await message.channel.send("Updated Markov!")

        elif message.content == "!update all" and message.author.id == adminid:
            await message.channel.send("Updating Markov on all channels...")
            total = 0
            for channel in message.guild.text_channels:
                try:
                    await message.channel.send("Updating Markov on channel " + channel.name + "...")
                    steps = markov.update_markovs(client, channel, message.created_at, yielddist=1000, yieldlog=1.5)
                    i = 0
                    async for i in steps:
                        await message.channel.send("Checked " + str(i) + " messages from channel " + channel.name + " (" + str(total + i) + " total)!")
                    total += i
                except discord.Forbidden:
                    await message.channel.send("Can't access " + channel.name + "; insufficient permissions")
                    
            await message.channel.send("Saving...")
            markov.save()

            await message.channel.send("Updated Markovs on all channels!")

        elif message.content == "!save" and message.author.id == adminid:
            markov.save()
            await message.channel.send("Markovs saved to disk successfully!")

        elif message.content == "!load" and message.author.id == adminid:
            markov.load()
            await message.channel.send("Markovs loaded from disk successfully!")

        elif message.content == "!delete" and message.author.id == adminid:
            markov.deleteFile()
            await message.channel.send("Deleted Markovs file!")
        
        elif message.content == "!quote":
            await message.channel.send(random.choice(quotes) if len(quotes) > 0 else "No quotes yet!")
        
        elif message.content.startswith("!quote "):
            quotes.append(message.content[7:].replace(configDelim, ""))
            save_config()
            await message.channel.send("Quote saved!")

        elif message.content.startswith("!math "):
            if message.author.id != adminid:
                await message.channel.send("This command is still in closed beta!")
                return
            
            try:
                val = str(eval(message.content[6:]))
            except Exception as e:
                val = "Error! " + str(e)
            await message.channel.send(val)
            
        elif message.content.startswith("!imitate"):
            spl = message.content.split()
            num = 1
            try:
                if len(spl) >= 2:
                    num = int(spl[1])
            except ValueError:
                pass
            if (num > 10):
                await message.channel.send("Argument may not exceed 10!")
            else:
                gen = ""
                while True:
                    gen = markov.markov_generate()
                    if len(gen.split()) >= num:
                        break
                await message.channel.send(gen)

        elif message.content == "!test":
            counter = 0
            tmp = await message.channel.send("Calculating messages...")
            async for log in message.channel.history(limit=100):
                if log.author == message.author:
                    counter += 1
            await tmp.edit(content="Your id is {} and you have {} messages.".format(message.author.id, counter))
            
        elif message.content == "!jsondump" and message.author.id == adminid:
            markov.json_dump()
            await message.channel.send("Dumped JSON! Check the console")

        elif message.content == "!sleep":
            await message.channel.send("sleeping now")
            await asyncio.sleep(5)
            await message.channel.send("!sleep done")

        elif message.content == "!inviteme":
            await message.channel.send("Invite me to your server: https://discord.com/api/oauth2/authorize?client_id=828567114007969853&permissions=2048&scope=bot")
            
        elif len(message.content) > 5 and message.content[0] == message.content[2] and message.content[0:3].islower() and message.content[3:5] == " x":
            print("lol-ing")
            arg = message.content[5:]
            num = None
            try:
                num = int(arg)
            except ValueError:
                await message.channel.send("Argument must be an integer!")
            if num is not None:
                if num > 500:
                    await message.channel.send("eh idk man, this situation isn't THAT funny")
                else:
                    msg = message.content[0].upper() + "".join(message.content[1].upper() for x in range(num)) + message.content[2].upper()
                    await message.channel.send(msg)
    except Exception:
        # restart the bot if an exception is raised to prevent invalid memory states
        stop_bot()




async def init_tellme():
    global tellme
    max = maxmsglen - 200
    sold = ""
    s = ""
    i = 0
    while (len(s) <= max):
        sold = s
        i += 1
        for j in range(0, i):
            s += "tell me"
        for j in range(0, i):
            s += " that"
        s += " "

    tellme = sold
    print("Initialized tellme")

async def init():
    markov.load()
    await asyncio.wait([init_tellme()])




async def start_bot():
    print()
    print()
    print()
    print(str(datetime.datetime.now()))
    print("Initializing bot...")
    await init()

        
def stop_bot():
    print("Saving before stopping...")
    markov.save()
    print("Quitting now....")
    quit()
    
def restart_bot():
    print("Restarting now...")
    python = sys.executable
    os.execl(python, python, * sys.argv)



print("Starting async task...")

loop = asyncio.get_event_loop()
loop.run_until_complete(start_bot())

print("Logging in...")
client.run(token)
