"""only these items should be used from outside"""
import logging
from .account import Account, AccountManager
from .connection.config import Config
from .storage.email.file import file_from_local, file_from_upload

__all__ = (
    'Account',
    'AccountManager',
    'Config',
    'file_from_local',
    'file_from_upload',
    )

NAME = 'imap-storage'
VERSION = '0.2.1'
DEBUG = False
