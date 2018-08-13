import discord
import asyncio
from random import randint
from threading import Thread
from time import sleep
import requests
import json

client = discord.Client()


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


@client.event
async def on_message(message):
    print(Colors.OKBLUE + "[!] got a message: " + message.content + Colors.ENDC)

    if message.content.startswith("!help"):
        await client.sendmessage(message.channel, "no help for you")
    elif len(message.content.split(" ")) != 1 and message.content.startswith("!word"):
        words = message.content.split(" ")[1:]
        words = "".join(word for word in words)
        words.replace(" ", "+")
        word, definition, example = get_word(words)
        send_message = 'Word: ' + word + '\nDefinition:\n"""\n' + definition + '\n"""\nExample:\n' + example
        await client.send_message(message.channel, send_message)

    elif message.content.startswith("!word"):
        word, definition, example = get_random_word()
        send_message = 'Word: ' + word + '\nDefinition:\n"""\n' + definition + '\n"""\nExample:\n' + example
        await client.send_message(message.channel, send_message)

    print(Colors.OKBLUE + "[!] sent message without errors" + Colors.ENDC)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def main():
    global client

    thread_discord = Thread(target=client.run, args=('bot token',)).start()


if __name__ == '__main__':
    main()
