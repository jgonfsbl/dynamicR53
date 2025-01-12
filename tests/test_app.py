#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Dynamic Route 53 Updater"""

__updated__ = "2025-01-12 23:44:47"


import json
import pytest
from src.dynr53.app import (main, get_aws_session, get_public_ip, get_route53_record_value)


def test_main():
    pass


if __name__ == "__main__":
    pytest.main()