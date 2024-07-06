# -*- coding: utf-8 -*-
"""
Community-developed Python SDK for interacting with Gamechanger APIs.
"""

import logging
import os

from .downloader import GameChangerDownloader
from .exceptions import ApiError
from .version import __version__

logging.basicConfig(format='%(asctime)s %(name)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv('LOG_LEVEL', logging.INFO))
