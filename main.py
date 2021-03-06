"""
Main crawler runner
"""

# standard
from urllib.parse import urlparse
from random import choice
from pathlib import Path
from shutil import rmtree
import asyncio
import sys

# pypi
# # playwright
from playwright.async_api import async_playwright, TimeoutError as PlwTimErr, Page
# # scrapy
from scrapy.utils.reactor import install_reactor
from scrapy.utils.project import Settings
from scrapy.crawler import CrawlerProcess
# # logger
from loguru import logger
# # faker
from faker import Faker
# # nested asyncio
import nest_asyncio

# local
from scraper_js.goosebumps.spiders import LarvaeSpider
from scraper_js.goosebumps import settings


# get scrapy settings
sts = Settings()
sts.setmodule(module=settings)

# install twisted reactor
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

# folder for browser storage
browser_cache: Path = Path(__file__).parent / 'dump/cache'
rmtree(browser_cache, ignore_errors=True)
browser_cache.mkdir(parents=True, exist_ok=True)
brw_cxt_store: Path = Path(browser_cache.parent, 'cxt_store.json')

# patch asyncio
nest_asyncio.apply()

fake = Faker()
Faker.seed(0)

header_ = {'User-Agent': choice([fake.user_agent() for _ in range(5)])}


def scrapy_process(s_url: str):
    """Scrapy process"""
    n_loc = urlparse(s_url).netloc
    f_pth = n_loc.replace('.', '-')

    # scrapy process
    scrapy_ps = CrawlerProcess(settings=sts)

    logger.trace('Configuring crawler')
    scrapy_ps.crawl(
        LarvaeSpider,
        allowed_domains=[n_loc, ],
        start_urls=[s_url, ],
        user_agent=header_['User-Agent'],
        url_dump_path=f'dump/{f_pth}.txt',
        file_store=brw_cxt_store,
    )
    logger.debug('Starting crawler')
    scrapy_ps.start()


async def login_action(page: Page) -> Page:
    """Login"""
    await page.locator('input[name=\"uid\"]').click()
    await page.locator('input[name=\"uid\"]').fill('admin')

    await page.locator('input[name=\"passw\"]').click()
    await page.locator('input[name=\"passw\"]').fill('admin')

    await page.locator('input:has-text(\"Login\")').click()
    return page


async def playwright_process():
    """Playwright process"""
    url = 'https://demo.testfire.net/login.jsp'
    try:
        async with async_playwright() as spw:
            logger.debug('Starting playwright')
            logger.trace('Instantiating browser & context')
            cxt_main = await spw.chromium.launch_persistent_context(  # launch(
                user_data_dir=browser_cache,
                ignore_https_errors=True,
                # headless=False,
            )
            # logger.trace('Creating new context')
            # cxt_main = await brw.new_context(ignore_https_errors=True)
            await cxt_main.set_extra_http_headers(header_)
            logger.trace('Opening new page')
            page = await cxt_main.new_page()
            logger.trace(f'Navigating to "{url}"')
            await page.goto(url)
            logger.debug('Logging in')
            home_page = await login_action(page)
            logger.success(f'login successful @ "{home_page.url}"')
            await cxt_main.storage_state(path=brw_cxt_store)
            scrapy_process(home_page.url)
            await cxt_main.close()
            # await brw.close()
    except (PlwTimErr, KeyboardInterrupt) as err:
        logger.error(f'{err}\n\nAborted.')


logger.remove()
logger.add(sys.stderr, level='TRACE')

asyncio.run(playwright_process())
rmtree(browser_cache, ignore_errors=True)
