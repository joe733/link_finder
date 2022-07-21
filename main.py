"""
Main crawler runner
"""

# standard
from urllib.parse import urlparse
from pathlib import Path
import asyncio
import sys

# pypi
# # scrapy
from scrapy.utils.reactor import install_reactor
from scrapy.utils.project import Settings
from scrapy.crawler import CrawlerProcess
# # playwright
from playwright.async_api import async_playwright, TimeoutError as PlwTimErr, Page
# # logger
from loguru import logger
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
browser_cache: Path = Path(__file__).parent / 'cache'
browser_cache.mkdir(parents=True, exist_ok=True)
brw_cxt_store: Path = Path(browser_cache, 'cxt_store.json')

# patch asyncio
nest_asyncio.apply()


def scrapy_process(s_url: str, page: Page):
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
        file_path=f'dump/{f_pth}.txt',
        # stored_state=brw_cxt_store,
        cache=browser_cache,
        page=page
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
    # 'https://www.kennedy-center.org/'
    # https://windowwonderland.withgoogle.com/
    # https://www.villesetpaysages.fr/
    # 'https://books.toscrape.com/'
    async with async_playwright() as spw:
        try:
            logger.debug('Starting playwright')
            cxt_main = await spw.chromium.launch_persistent_context(
                user_data_dir=browser_cache,
                ignore_https_errors=True,
            )
            # logger.trace('Creating new browser context')
            # cxt_main = await brw.new_context(ignore_https_errors=True)
            logger.trace('Opening new page')
            page = await cxt_main.new_page()
            logger.trace(f'Navigating to "{url}"')
            await page.goto(url)
            logger.debug('Logging in')
            home_page = await login_action(page)
            logger.success(f'login successful @ "{home_page.url}"')
            await cxt_main.storage_state(path=brw_cxt_store)
            scrapy_process(home_page.url, home_page)
            await cxt_main.close()
            # await brw.close()
        except PlwTimErr as err:
            logger.error(f'{err}')


logger.remove()
logger.add(sys.stderr, level='TRACE')

asyncio.run(playwright_process())
