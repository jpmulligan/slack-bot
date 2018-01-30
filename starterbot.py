# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 20:43:02 2018

@author: jpmul
"""

import configparser
import time
import re
from slackclient import SlackClient


# Using a tiny config.ini file, this needs to exist to work
# Need to put OAuth token in there under [DEFAULT] heading
# Should probably use environment variables instead, but whatever 
config = configparser.ConfigParser()
config.read('config.ini')

# Creating an instance of slack client using the token from config.ini
slack_client = SlackClient(config['DEFAULT']['SlackBotToken'])
starterbot_id = None

RTM_READ_DELAY = 1 # Delay for time.slee() in seconds to slow down main loop
MENTION_REGEX = "^<@(|[WU].+)>(.*)" # this might as well be line noise


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    #print(slack_events)
    for event in slack_events:
        if event["type"] == "hello":
            print("Got hello event!")
        elif event["type"] == "message" and not "subtype" in event:
            print(event['ts'], event['channel'], event['user'], event['text'])
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    print("HANDLER: ", command, channel)

    # COMMAND: HELP
    if command.startswith("help"):
        wall("I don't do much yet. No help available.")

    # COMMAND: CHANNELS
    elif command.startswith("channels"):
        channel_list = slack_client.api_call("channels.list")['channels']
        
        joined_chans = []
        for chan in channel_list:
            if chan['is_member'] is True:
                joined_chans.append(chan['name'])

        response = f"I found {len(channel_list)} channels. "
        response += f"I'm a member of the following: {','.join(joined_chans)}"
        wall(response)

    # COMMAND: USERS
    elif command.startswith("users"):
        list_users()

    # COMMAND: WALL        
    elif command.startswith("wall"):
        message = ' '.join(command.split()[1:])
        wall(message)

    # DEFAULT RESPONSE
    else:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="Instructions unclear."
        )

def list_users():
    users = slack_client.api_call("users.list")['members']
    for user in users:
        print(user['id'], user['name'], user['real_name'])
    wall(len(users))
    

def wall(message):
    print(f"Sending {message} to all joined channels...")
    channel_list = slack_client.api_call("channels.list")['channels']
    for chan in channel_list:
        if chan['is_member'] is True:
            print(chan['name'])
            slack_client.api_call(
                "chat.postMessage",
                channel=chan['id'],
                text=message
            )

def wallme(message):
    print(f"Sending {message} to all joined channels...")
    channel_list = slack_client.api_call("channels.list")['channels']
    for chan in channel_list:
        if chan['is_member'] is True:
            print(chan['name'])
            slack_client.api_call(
                "chat.meMessage",
                channel=chan['id'],
                text=message
            )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Bot RTM connect successful!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        starterbot_user = slack_client.api_call("auth.test")["user"]
        print("BOT ID:\t", starterbot_id)
        print("BOT USER:\t", starterbot_user)

        # What channels am I a member of?
        channel_list = slack_client.api_call("channels.list")['channels']
        bot_channels = []
        for chan in channel_list:
            if chan['is_member'] is True:
                print(f"Joined: {chan['name']}:{chan['id']}")
                bot_channels.append(chan['id'])
        print(f"I'm a member of {len(bot_channels)} channel(s).")

        wallme("Bzzzzzzzzzzzzzrtttttt.....")

        print("Starting main loop....")
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                print("Got a command!", command, channel)
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
        
        