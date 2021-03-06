import discord
import asyncio
import threading
from random import randint
from random import randrange
from datetime import datetime
import requests
import json


API = False
api = None
try:
    import api
    from api import Posts, Post
    API = False
    api = api.Api()
except ImportError:
    print("PR0 API NOT AVAILABLE")

client = discord.Client()
auto_channel = None

# change to true if you want autoposting enabled
AUTOPOSTING = False
AUTOPOSTTAGS = ["meme", "python", "java", "comic", "programming", "/r/ProgrammerHumor", "greentext"]

# blacklist of tags that should not be included in auto-post
BLACKLIST = ["hitler", "nazi", "propaganda", "fake news", "nazinostalgie", "schlauchkefer", '"sfw"', "stratham", "earthporn"]
# note that tags like 'gore' are not included because they are filtered out
# by the flag. Auto-post only uses sfw (safe for work)

GR_RUNNING = False
GR_MESSAGE = None
GRUPPENTHERAPIE = []

# put the bot token here
TOKEN = 'bot-token'


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_random_word():
    response = requests.get("http://api.urbandictionary.com/v0/random")
    json_response = json.loads(response.content.decode('utf-8'))
    word_definition = json_response["list"][randint(0, len(json_response["list"]) - 1)]
    print(word_definition)
    return word_definition['word'], word_definition['definition'], word_definition['example']


def get_word(word):
    response = requests.get("http://api.urbandictionary.com/v0/define?term={" + word + "}")
    json_response = json.loads(response.content.decode('utf-8'))
    print(json_response)
    word_definition = json_response["list"][randint(0, len(json_response["list"]) - 1)]
    print(word_definition)
    return word_definition['word'], word_definition['definition'], word_definition['example']


def parse_pr0_command(msg):
    global api

    flags = api.calculate_flag(
        sfw=True if not "no-sfw" in msg.content else False,
        nsfw=True if "nsfw" in msg.content else False,
        nsfl=True if "nsfl" in msg.content else False,
        nsfp=True if "nsfp" in msg.content else False
    )

    print("FLAG: " + str(flags))

    tags = ""
    if '"' in msg.content:
        tags = msg.content.split('"')[-2]
    else:
        tags = msg.content.split(' ')[-1]

    max = int(json.loads(api.get_newest_image(flags))["id"])

    all_posts = Posts()
    for posts in api.get_items_by_tag_iterator(tags=tags, flag=flags):
        all_posts.extend(posts)
        if randrange(0, 100) > 90:
            break

    send_post = all_posts[randrange(0, len(all_posts))]
    return "https://img.pr0gramm.com/" + str(send_post["image"])


async def gruppentherapie(message):
    global GR_RUNNING
    global GR_MESSAGE  # currently not used
    global GRUPPENTHERAPIE

    parsed_msg = message.content.split(" ")

    if len(parsed_msg) == 1:
        if GR_RUNNING:
            for i in range(0, len(GRUPPENTHERAPIE)*20):
                rand_a = randrange(0, len(GRUPPENTHERAPIE))
                rand_b = randrange(0, len(GRUPPENTHERAPIE))
                GRUPPENTHERAPIE[rand_a], GRUPPENTHERAPIE[rand_b] = GRUPPENTHERAPIE[rand_b], GRUPPENTHERAPIE[rand_a]
            GRUPPENTHERAPIE.insert(0, "Gruppentherapie!\n")
            await message.channel.send("".join(name + "\n" for name in GRUPPENTHERAPIE))
            del GRUPPENTHERAPIE[0]
    elif parsed_msg[1] == "start":
        GRUPPENTHERAPIE.insert(0, "Gruppentherapie!\n")
        await message.channel.send("".join(name + "\n" for name in GRUPPENTHERAPIE))
        del GRUPPENTHERAPIE[0]
        GR_RUNNING = True
    elif parsed_msg[1] == "add":
        GRUPPENTHERAPIE.append("".join(name + " " for name in parsed_msg[2:])[:-1])
        await message.channel.send("Added " + GRUPPENTHERAPIE[-1])

        if GR_RUNNING:
            GRUPPENTHERAPIE.insert(0, "Gruppentherapie!\n")
            GR_MESSAGE = await message.channel.send("".join(name + "\n" for name in GRUPPENTHERAPIE))
            del GRUPPENTHERAPIE[0]
    elif parsed_msg[1] == "stop":
        await message.channel.send("ende der Gruppentherapie :(")
        GR_RUNNING = False
        GR_MESSAGE = None
        GRUPPENTHERAPIE = []


@client.event
async def on_message(message):
    print(Colors.OKGREEN + "[!] got a message: " + message.content + Colors.ENDC)

    if message.content.startswith("!help"):
        await message.channel.send('no help for you')
    elif len(message.content.split(" ")) != 1 and message.content.startswith("!word"):
        words = message.content.split(" ")[1:]
        words = "".join(word + "+" for word in words)
        words = words[0:-1]
        word, definition, example = get_word(words)
        send_message = 'Word: ' + word + '\nDefinition:\n"""\n' + definition + '\n"""\nExample:\n' + example
        await message.channel.send(send_message)

    elif message.content.startswith("!word"):
        word, definition, example = get_random_word()
        send_message = 'Word: ' + word + '\nDefinition:\n"""\n' + definition + '\n"""\nExample:\n' + example
        await message.channel.send(send_message)
    elif message.content.startswith("!pr0"):
        await message.channel.send(parse_pr0_command(message))
    elif message.content.startswith("!syntax"):
        send_message = "Syntax for command '!pr0':\n" \
                       + """command ::= "!pr0" "no-sfw"? "nsfw"? "nsfl"? "nsfp"? (tag | tags)
                            tag ::= ([A-Z] | [a-z] | [0-9])*
                            tags ::= '"' (tag " ")+  '"'"""
        await message.channel.send(send_message)
    elif message.content.lower().startswith("!gruppentherapie") or message.content.lower().startswith("!gr"):
        await gruppentherapie(message)
    elif message.content.lower().startswith("!d"):
        dice = int(message.content.split("d")[1])+1
        number = 0
        print("generating random number for: " + str(dice-1))
        for i in range(0, randint(10, 1000)):
            number = str(randrange(1, (dice*10)//10))
        await message.channel.send(number)

    print(Colors.OKGREEN + "[!] sent message without errors" + Colors.ENDC)


@client.event
async def on_ready():
    global auto_channel
    global BLACKLIST
    global AUTOPOSTING
    global AUTOPOSTTAGS

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    if not AUTOPOSTING:
        return

    for channel in client.get_all_channels():
        if channel.name == "bot-autopost":
            print("[!] found autopost channel")
            auto_channel = channel
            break

    while True:
        if datetime.now().minute == 0:
            all_posts = Posts()

            for tag in AUTOPOSTTAGS:
                for post in api.get_items_by_tag_iterator(tags=tag):
                    all_posts.extend(post)
                    if len(all_posts) > 500:
                        break

            # eliminate bad posts
            new_posts = Posts()
            for post in all_posts:
                if post["up"] - post["down"] > 30:
                    new_posts.append(post)

            print("[!] len before elimination: " + str(len(all_posts)))
            all_posts = new_posts
            print("[!] len after elimination: " + str(len(all_posts)))

            blacklisted = True
            tags = ""
            post = []
            while blacklisted:
                await asyncio.sleep(1)
                blacklisted = False
                post = all_posts[randrange(0, len(all_posts))]
                tags = json.loads(api.get_item_info(post["id"]))["tags"]

                for tag in tags:
                    splitted_tag = tag["tag"].lower().split(" ")
                    for tag_word in splitted_tag:
                        if tag_word in BLACKLIST:
                            blacklisted = True
                            print("POST IS BLACKLISTED BECAUSE OF " + tag_word)

            print("POSTING: ")
            print(post)
            print("with tags: " + str(tags))
            await auto_channel.send("https://img.pr0gramm.com/" + post["image"])
        while 23 == datetime.now().hour or datetime.now().hour < 7:
            await asyncio.sleep(50)
        await asyncio.sleep(50)


async def start():
    await client.start(TOKEN) # use client.start instead of client.run


def run_it_forever(loop):
    loop.run_forever()


def init():
    global client

    asyncio.get_child_watcher()  # uh this function sound weird

    loop = asyncio.get_event_loop()
    loop.create_task(start())

    thread = threading.Thread(target=run_it_forever, args=(loop,))
    thread.start()


if __name__ == '__main__':
    init()
