"""
Main crawler runner
"""

# pypi
from scrapy.utils.reactor import install_reactor
from scrapy.utils.project import Settings
from scrapy.crawler import CrawlerProcess

# local
from scraper_js.goosebumps.spiders import LarvaeSpider
from scraper_js.goosebumps import settings


# get scrapy settings
sts = Settings()
sts.setmodule(module=settings)

# install twisted reactor
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

# scrapy process
scrapy_ps = CrawlerProcess(settings=sts)
scrapy_ps.crawl(
    LarvaeSpider,
    allowed_domains='scrapethissite.com',
    start_urls='https://www.scrapethissite.com/',
    file_path='dump/scrapethissite-com-js.txt',
)
scrapy_ps.start()
