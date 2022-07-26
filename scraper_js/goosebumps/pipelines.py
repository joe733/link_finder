"""
Define your item pipelines here

Don't forget to add your pipeline to the ITEM_PIPELINES setting

See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

# standard
from typing import IO, Any
from pathlib import Path

# pypi
from scrapy.spiders import Spider
from scrapy.item import Item


class GoosebumpsPipeline:
    """Goosebumps pipeline"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize goosebumps pipeline"""
        super().__init__(*args, **kwargs)
        self.file: IO

    def open_spider(self, spider: Spider) -> None:
        """When spider is opened"""
        file_path: Path = Path(
            flp if (
                flp := getattr(spider, 'url_dump_path', None)
            ) else 'default-url-dump.txt'
        )
        self.file = file_path.open(
            mode=getattr(spider, 'file_mode', None) or 'w',
            encoding=getattr(spider, 'file_encoding', None) or 'utf-8'
        )

    def close_spider(self, spider: Spider) -> None:
        """When spider is closed"""
        self.file.close()
        del spider

    def process_item(self, item: Item, spider: Spider) -> Item:
        """Write processed item to file"""
        self.file.write(f'{item.url}\n')
        del spider
        return item
