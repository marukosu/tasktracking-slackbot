# -*- coding: utf-8 -*-
import os

API_TOKEN = os.environ['TEST_SLACKBOT_API_TOKEN']


PLUGINS = [
    'plugins',
]

ERRORS_TO = 'bot_errors'
default_reply = "Your message is not supported, please see help(just comment 'help')"
