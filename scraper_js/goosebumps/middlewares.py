"""
Scrapy Middleware

Define here the models for your spider middleware

See documentation in:
https://docs.scrapy.org/en/latest/topics/spider-middleware.html
"""

# standard
from typing import Any, Generator

# pypi
# # typing
from typing_extensions import Self
# # scrapy
from scrapy.http import Request, Response
from scrapy.crawler import Crawler
from scrapy.spiders import Spider
from scrapy import signals
# useful for handling different item types with a single interface
# from itemadapter import is_item, ItemAdapter


class GoosebumpsSpiderMiddleware:
    """Goosebumps Spider Middleware"""
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        """This method is used by Scrapy to create your spiders."""
        cls_ = cls()
        crawler.signals.connect(
            cls_.spider_opened, signal=signals.spider_opened
        )
        return cls_

    def process_spider_input(self, response: Response, spider: Spider) -> None:
        """
        Called for each response that goes through the spider
        middleware and into the spider.

        Should return None or raise an exception.
        """
        del response, spider

    def process_spider_output(
        self, response: Response, result: Any, spider: Spider
    ) -> Generator[Any, None, None]:
        """
        Called with the results returned from the Spider, after
        it has processed the response.

        Must return an iterable of Request, or item objects.
        """
        del response, spider
        yield from result

    def process_spider_exception(
        self, response: Response, exception: Exception, spider: Spider
    ) -> None:
        """
        Called when a spider or process_spider_input() method
        (from other spider middleware) raises an exception.

        Should return either None or an iterable of Request or item objects.
        """
        del response, exception, spider

    def process_start_requests(
        self, start_requests: Request, spider: Spider
    ) -> Generator[Any, None, None]:
        """
        Called with the start requests of the spider, and works
        similarly to the process_spider_output() method, except
        that it doesn't have a response associated.

        Must return only requests (not items).
        """
        del spider
        yield from start_requests

    def spider_opened(self, spider: Spider) -> None:
        """Log opened spider"""
        spider.logger.info(f'Spider opened: {spider.name}')


class GoosebumpsDownloaderMiddleware:
    """Goosebumps Downloader Middleware"""
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        """This method is used by Scrapy to create your spiders."""
        cls_ = cls()
        crawler.signals.connect(
            cls_.spider_opened, signal=signals.spider_opened
        )
        return cls_

    def process_request(self, request: Request, spider: Spider) -> None:
        """
        Called for each request that goes through the downloader
        middleware.

        Must either:
        - return None: continue processing this request
        - or return a Response object
        - or return a Request object
        - or raise IgnoreRequest: process_exception() methods of
          installed downloader middleware will be called
        """
        del request, spider

    def process_response(self, request: Request, response: Response, spider: Spider) -> Response:
        """
        Called with the response returned from the downloader.

        Must either;
        - return a Response object
        - return a Request object
        - or raise IgnoreRequest
        """
        del request, spider
        return response

    def process_exception(self, request: Request, exception: Exception, spider: Spider) -> None:
        """
        Called when a download handler or a process_request()
        (from other downloader middleware) raises an exception.

        Must either:
        - return None: continue processing this exception
        - return a Response object: stops process_exception() chain
        - return a Request object: stops process_exception() chain
        """
        del request, exception, spider

    def spider_opened(self, spider: Spider) -> None:
        """Log opened spider"""
        spider.logger.info(f'Spider opened: {spider.name}')
