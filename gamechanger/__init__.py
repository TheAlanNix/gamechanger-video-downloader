# -*- coding: utf-8 -*-
"""
Community-developed Python SDK for interacting with Gamechanger APIs.
"""

import logging
import os

from .downloader import GameChangerDownloader  # noqa: F401
from .exceptions import ApiError  # noqa: F401
from .version import __version__  # noqa: F401

logging.basicConfig(format='%(asctime)s %(name)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv('LOG_LEVEL', logging.INFO))
