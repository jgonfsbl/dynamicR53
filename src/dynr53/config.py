#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Dynamic Route 53 Updater"""

__updated__ = "2025-01-12 23:45:04"


from os import environ
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class Config:
    """
    Set configuration vars from .env file or environment variables
    """
    HOSTED_ZONE_ID = environ.get("HOSTED_ZONE_ID", None)
    RECORD_NAME = environ.get("RECORD_NAME", None)
    TTL = environ.get("TTL", 300)
