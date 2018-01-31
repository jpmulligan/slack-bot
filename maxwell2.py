# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 21:30:30 2018

@author: jpmul
"""

import configparser
import time
from slackclient import SlackClient

class SlackBot(object):
    
    def __init__(self, config):
        self.config = config
        self.user_id = None
        self.user = None
        self.apitoken = config['DEFAULT']['SlackBotToken']
        self.read_delay = int(config['DEFAULT']['ReadDelay'])
        self.client = SlackClient(config['DEFAULT']['SlackBotToken'])
        self.logging = False
    
    def connect(self):
        if self.client.rtm_connect(with_team_state=False):
            auth_test = self.client.api_call("auth.test")
            self.user_id = auth_test['user_id']
            self.user = auth_test['user']

    def delay(self):
        time.sleep(self.read_delay)
        return
 
    def parse_events(self):
        
        events = self.client.rtm_read()
        for event in events:
            if event['type'] == 'message':
                
                if event['text'].find(f'<@{self.user_id}> ') != -1:
                    print(event)
                    self.parse_dm(event)
                    
                elif event['channel'].startswith('D'):
                    self.parse_dm(event)
                
                elif self.logging is True:
                    print(f"{event['ts']}: {event['text']}")
                    
                else:
                    return

    def parse_dm(self, event):

        message = event['text'].strip(f'<@{self.user_id}> ')
        cmd = message.split()[0]
        if len(message.split()) > 1:
            arg = message.split()[1]
        else:
            arg = None
            
        if cmd == 'log':
            print(f"self.log = {self.log(arg)}")

        elif cmd == 'botid':
            print(f"self.user_id = {self.user_id}")
            print(f"self.user = {self.user}")

        else:
            print("Instructions unclear.")
        
    def log(self, status):
        if status == 'on':
            self.logging = True
        else:
            self.logging = False
        return self.logging

if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read('config.ini')
    bot = SlackBot(config)
    bot.connect()
    print(f"Connected as {bot.user_id}, starting main loop...")
    while True:
        bot.parse_events()
        bot.delay()
            
    
