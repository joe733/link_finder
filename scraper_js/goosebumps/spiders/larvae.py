"""
Larvae Crawler Spider

NOTE: This script contains a CrawlSpider,
built with an incomplete understanding
of the documentation. Hence, please pardon
mistakes, if any.
"""

# standard
from typing import Generator, Sequence
from contextlib import suppress
from platform import system

# pypi
# # scrapy
from scrapy.linkextractors import LinkExtractor, IGNORED_EXTENSIONS
from scrapy.utils.url import canonicalize_url
from scrapy.dupefilters import RFPDupeFilter
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Response, Request
# # twisted
from twisted.python.failure import Failure  # just for typing
# # loguru
from loguru import logger

# local
# # scrapy-item
from scraper_js.goosebumps.items import GoosebumpsLinkItem


# pylint: disable = abstract-method
class LarvaeSpider(CrawlSpider):
    """Larvae crawler spider"""
    name: str = 'larvae'

    def __init__(self, *a, **kw,) -> None:
        """Initialize larvae crawler spider"""
        super().__init__(*a, **kw)
        self.custom_settings: dict | None = {
            'AUTO_THROTTLE_ENABLED': True,
            'DUPEFILTER_CLASS': RFPDupeFilter,
        }

        # allowed_domain
        if isinstance(awd := kw.get('allowed_domains'), list):
            self.allowed_domains: list[str] = awd
        elif isinstance(awd, str):
            self.allowed_domains: list[str] = [awd, ]
        else:
            raise TypeError('Unknown type for allowed-domains')

        # start_urls
        if isinstance(stu := kw.get('start_urls'), list):
            self.start_urls: list[str] = stu
        elif isinstance(stu, str):
            self.start_urls: list[str] = [stu, ]
        else:
            raise TypeError('Unknown type for start-urls')

        self.lnk_xtr = LinkExtractor(
            allow_domains=self.allowed_domains,
            deny=r'logout',
            deny_extensions=IGNORED_EXTENSIONS
        )
        self.rules: Sequence[Rule] = (
            Rule(
                self.lnk_xtr,
                callback='parse_item',
                follow=True,
            ),
        )

        self.headers = {}
        # cookies if required
        if cks := kw.get('cookie'):
            if not isinstance(cks, str):
                raise TypeError('Unable to set cookies')
            self.headers['cookie'] = cks

        # user-agent if required
        if usr_agt := kw.get('user_agent'):
            if not isinstance(usr_agt, str):
                raise TypeError('Unable to set user-agent')
            self.headers['User-Agent'] = usr_agt

        self.unique_urls = set(self.start_urls)
        self.link_list = []

        # request meta config
        self.rq_meta = {
            'dont_merge_cookies': True,
            'handle_httpstatus_list': [404, 302],
            'playwright': system().lower() in {'linux', 'darwin'},
            'playwright_context': 'new_local',
            'playwright_context_kwargs': {
                # 'user_data_dir': kw.get('cache_dir'),
                'stored_state': kw.get('file_store'),
                'ignore_https_errors': True,
            },
            'playwright_page': kw.get('page'),
        }

    def start_requests(self) -> Generator[Request, None, None]:
        """Start scrapy requests"""
        for url_ in self.start_urls:
            yield Request(
                url=url_,
                headers=self.headers or None,
                callback=self.parse_item,
                meta=self.rq_meta,
                errback=self.spider_error,
            )

    def parse_item(self, response: Response) -> Generator[
        GoosebumpsLinkItem | Request, None, None
    ]:
        """Parse scrapy items"""
        with suppress(AttributeError):
            # masks error when url points to non-text entities
            for link in self.lnk_xtr.extract_links(response):
                cz_url = str(canonicalize_url(link.url)).rstrip('/')
                if cz_url not in self.unique_urls:
                    if response.status == 200:
                        self.link_list.append(
                            link_item := GoosebumpsLinkItem(
                                url=cz_url,
                                status_code=response.status,
                                text=link.text,
                                fragment=link.fragment,
                                nofollow=link.nofollow
                            )
                        )
                        yield link_item  # yields link-item to the pipeline
                    self.unique_urls.add(cz_url)
                    yield response.follow(
                        url=link.url,
                        headers=self.headers or None,
                        callback=self.parse_item,
                        meta=self.rq_meta,
                        errback=self.spider_error,
                    )

    def spider_error(self, failure: Failure):
        """Catch and display errors gracefully"""
        logger.error(
            f'{type(failure.value).__name__} •'
            + f' {failure.request} •'
            + f' {failure.value}\n'
            + f' {failure.getTraceback()}'
        )
