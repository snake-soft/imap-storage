"""only these items should be used from outside"""
import logging
from .account import Account, AccountManager
from .connection.config import Config
from .storage.email.file import *

__all__ = ('Account', 'AccountManager', 'NAME', 'VERSION', 'DEBUG')

NAME = 'imap-storage'
VERSION = '0.2.0'
DEBUG = False

#logging.basicConfig(
#    filename='/var/log/' + NAME + '.log',
#    level=logging.DEBUG if DEBUG else logging.INFO,
#    )
