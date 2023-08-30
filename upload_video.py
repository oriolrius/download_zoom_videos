#!/usr/bin/env python3
import os
import sys
import logging
import structlog
from dotenv import load_dotenv
from pytion import Notion
from pytion.models import Block


# Load .env file
load_dotenv()

level = os.environ.get("LOG_LEVEL", "DEBUG").upper()
LOG_LEVEL = getattr(logging, level)

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL))
logger = structlog.get_logger()

token_v2 = os.getenv('NOTION_TOKEN_V2', '')
logger.debug(f'NOTION_TOKEN_V2: {token_v2}')

no = Notion(token=token_v2)
page = no.pages.get("8ba7f67d8e564cca8c315606f5482b92")  # retrieve page data (not content) and create object
logger.debug(f'page: {page}')

blocks = page.get_block_children()  # retrieve page content and create list of objects
logger.debug(f'blocks: {blocks}')

my_text_block = Block.create("Hello World!")
my_text_block = Block.create(text="Hello World!", type_="paragraph")  # the same
page.block_append(block=my_text_block)

my_file = Block.create(type_="file", file="./README.md")