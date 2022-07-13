"""
Scrapy Items

Define here the models for your scraped items

See documentation in:
https://docs.scrapy.org/en/latest/topics/items.html
"""

# standard
from dataclasses import dataclass


@dataclass
class GoosebumpsLinkItem:
    """Goosebumps link item"""
    url: str
    status_code: int
    text: str
    fragment: str
    nofollow: bool
