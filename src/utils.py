"""Utility functions for jobringer scraper."""
import asyncio
from urllib.parse import urlparse
from camoufox.async_api import AsyncCamoufox


def _parse_proxy(proxy_url):
    """Parse Apify proxy URL into components."""
    if not proxy_url:
        return None
    
    parsed = urlparse(proxy_url)
    return {
        'server': f'{parsed.scheme}://{parsed.hostname}:{parsed.port}',
        'username': parsed.username,
        'password': parsed.password
    }


async def _fetch(url, proxy_url=None):
    """Fetch page content using Camoufox browser."""
    proxy_config = _parse_proxy(proxy_url) if proxy_url else None
    
    async with AsyncCamoufox(
        headless=True,
        geoip=True,
        proxy=proxy_config
    ) as browser:
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=90000)
            await page.wait_for_timeout(3000)
            
            content = await page.content()
            
            if len(content) < 500:
                return None
            
            return content
            
        except Exception as e:
            print(f'Error fetching {url}: {e}')
            return None
        finally:
            await page.close()
