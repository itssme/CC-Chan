import discord
import asyncio
from random import randint
from threading import Thread
from time import sleep
from random import randrange
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


@client.event
async def on_message(message):
    print(Colors.OKBLUE + "[!] got a message: " + message.content + Colors.ENDC)

    if message.content.startswith("!help"):
        await client.sendmessage(message.channel, "no help for you")
    elif len(message.content.split(" ")) != 1 and message.content.startswith("!word"):
        words = message.content.split(" ")[1:]
        words = "".join(word + "+" for word in words)
        words = words[0:-1]
        word, definition, example = get_word(words)
        send_message = 'Word: ' + word + '\nDefinition:\n"""\n' + definition + '\n"""\nExample:\n' + example
        await client.send_message(message.channel, send_message)

    elif message.content.startswith("!word"):
        word, definition, example = get_random_word()
        send_message = 'Word: ' + word + '\nDefinition:\n"""\n' + definition + '\n"""\nExample:\n' + example
        await client.send_message(message.channel, send_message)
    elif message.content.startswith("!pr0"):
        await client.send_message(message.channel, parse_pr0_command(message))
    elif message.content.startswith("!syntax"):
        send_message = "Syntax for command '!pr0':\n" \
                       + """command ::= "!pr0" "no-sfw"? "nsfw"? "nsfl"? "nsfp"? (tag | tags)
                            tag ::= ([A-Z] | [a-z] | [0-9])*
                            tags ::= '"' (tag " ")+  '"'"""
        await client.send_message(message.channel, send_message)

    print(Colors.OKBLUE + "[!] sent message without errors" + Colors.ENDC)


@client.event
async def on_ready():
    global auto_channel

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    for server in client.servers:
        for channel in server.channels:
            if channel.name == "bot-autopost":
                print("[!] found autopost channel")
                auto_channel = channel
                break

    while True:
        all_posts = Posts()
        for post in api.get_items_by_tag_iterator(tags="meme"):
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

        post = all_posts[randrange(0, len(all_posts))]
        await client.send_message(auto_channel, "https://img.pr0gramm.com/" + post["image"])
        await asyncio.sleep(60*60)


def main():
    global client

    thread_discord = Thread(target=client.run, args=('bot token',)).start()


if __name__ == '__main__':
    main()
