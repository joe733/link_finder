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
from time import sleep

# pypi
from scrapy.linkextractors import LinkExtractor, IGNORED_EXTENSIONS
from scrapy.dupefilters import RFPDupeFilter
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Response, Request

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

        # cookies if required
        if cks := kw.get('cookie'):
            if isinstance(cks, str):
                self.headers = {'cookie': cks}
            else:
                raise TypeError('Unable to set cookies')
        else:
            self.headers = None

        self.unique_urls = set(self.start_urls)
        self.link_list = []

    def start_requests(self) -> Generator[Request, None, None]:
        """Start scrapy requests"""
        sleep(0.13)
        for url_ in self.start_urls:
            yield Request(
                url=url_,
                headers=self.headers,
                callback=self.parse_item,
                dont_filter=True,
                meta={'playwright': True}
            )

    def parse_item(self, response: Response) -> Generator[
        GoosebumpsLinkItem | Request, None, None
    ]:
        """Parse scrapy items"""
        sleep(0.13)
        with suppress(AttributeError):
            # masks error when url points to non-text entities
            for link in self.lnk_xtr.extract_links(response):
                if link.url not in self.unique_urls:
                    if response.status == 200:
                        self.link_list.append(
                            link_item := GoosebumpsLinkItem(
                                url=link.url,
                                status_code=response.status,
                                text=link.text,
                                fragment=link.fragment,
                                nofollow=link.nofollow
                            )
                        )
                        yield link_item  # yields link-item to the pipeline
                    self.unique_urls.add(link.url)
                    sleep(0.13)
                    yield response.follow(
                        url=link.url,
                        headers=self.headers,
                        callback=self.parse_item,
                        dont_filter=True,
                        meta={'playwright': True}
                    )
