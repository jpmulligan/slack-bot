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
bot_id = None

RTM_READ_DELAY = 1 # Delay for time.slee() in seconds to slow down main loop
MENTION_REGEX = "^<@(|[WU].+)>(.*)" # this might as well be line noise


def bot_rtm_events(slack_events):
    
    for event in slack_events:

        if event["type"] == "message" and not "subtype" in event:
            matches = re.search(MENTION_REGEX, event["text"])
            if matches:
                user_id, message = (matches.group(1), matches.group(2).strip())
            else:
                user_id, message = [None, None]
            if user_id == bot_id:
                print(f"Got a direct message: {message}")
            
    return None

def parse_direct_mention(message_text):

    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def bot_command(command, channel):
    
    print("HANDLER: ", command, channel)

def bot_channels(user_id):

    channels = slack_client.api_call("channels.list")['channels']
    bot_channels = []
    for channel in channels:
        if channel['is_member'] is True:
            bot_channels.append(channel['id'])
    if len(bot_channels) > 0:
        return bot_channels
    else:
        return None


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        bot_id = slack_client.api_call("auth.test")["user_id"]
        print(f"Connected to Slack as user id {bot_id}.")

        while True:
            bot_rtm_events(slack_client.rtm_read())

            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
        
        