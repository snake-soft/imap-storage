"""only these items should be used from outside"""
import logging
from .account import Account, AccountManager
from .connection.config import Config
from .storage.email.file import *

NAME = 'imap-storage'
VERSION = '0.2.0b4'
DEBUG = False

logging.basicConfig(
    filename=NAME + '.log',
    level=logging.DEBUG if DEBUG else logging.INFO,
    )
