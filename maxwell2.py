# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 21:30:30 2018

@author: jpmul
"""

import configparser
import time


from slackclient import SlackClient

class SlackBot(object):
    
    def __init__(self, config_file):
        
        print("Loading bot config...")
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.user_id = None
        self.user = None
        self.read_delay = int(self.config['DEFAULT']['ReadDelay'])
        self.client = SlackClient(self.config['DEFAULT']['SlackBotToken'])
        self.logging = False
        self.update_users()
        #self.send_me("Bbbrrrrrrrrrrrrzzzzzzzztttttttttttttttt.......")

        open('logfile.log', 'a')
    
    def connect(self):
        print("Attempting RTM connection... ", end="")
        if self.client.rtm_connect(with_team_state=False):
            auth_test = self.client.api_call("auth.test")
            self.user_id = auth_test['user_id']
            self.user = auth_test['user']
            print(f"RTM connection established as {bot.user_id}.")

    def delay(self):
        time.sleep(self.read_delay)
        return

    def update_users(self):
        self.users = self.client.api_call("users.list")
        print(f"Updated team user list with {len(self.users['members'])} members.")
        for user in self.users['members']:
            print(user['id'], user['name'], user['real_name'])
        

    def send_me(self, message):
        channel_list = self.client.api_call("channels.list")['channels']
        for chan in channel_list:
            if chan['is_member'] is True:
                self.client.api_call("chat.meMessage", channel=chan['id'], text=message)
 
    def send_pm(self, user, message=None):
        channel = f"@{user}"
        self.client.api_call("chat.postMessage", channel=channel, text=message, as_user='true')
    
    def parse_events(self):
        
        events = self.client.rtm_read()
        for event in events:
            if event['type'] == 'message' and event['user'] != self.user_id:

                if event['text'].find(f'<@{self.user_id}> ') != -1:
                    print(event)
                    self.parse_dm(event)
                    
                elif event['channel'].startswith('D'):
                    self.parse_dm(event)
                
                elif self.logging is True:
                    # Need to send this to a file instead of stdout
                    # But found out it's easier just to export Slack channel history to JSON dump
                    print(f"{event['ts']} | {event['channel']} | {event['user']} | {event['text']}")
                    
            else:
                return

    def parse_dm(self, event):

        user = event['user']
        message = event['text'].strip(f'<@{self.user_id}> ')
        
        cmd = message.split()[0]
        if len(message.split()) > 1:
            arg = message.split()[1]
        else:
            arg = None
            
        if cmd == 'log' and arg in ['on', 'off']:
            self.send_pm(user, message=f"self.log = {self.log(arg)}")

        elif cmd == 'botid':
            self.send_pm(user, message=f"self.user_id = {self.user_id}")
            self.send_pm(user, message=f"self.user = {self.user}")

        elif cmd == 'users':
            bot.update_users()
            self.send_pm(user, f"Updated team user list with {len(self.users['members'])} users.")

        else:
            print("Instructions unclear.")
        
    def log(self, status):
        if status == 'on':
            self.logging = True
        else:
            self.logging = False
        return self.logging

if __name__ == "__main__":

    bot = SlackBot('config.ini')
    bot.connect()

    print("Starting main loop...")
    while True:
        bot.parse_events()
        bot.delay()
            
    
