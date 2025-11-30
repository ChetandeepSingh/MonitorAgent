"""
Automatic Stream URL Refresher
Uses Playwright (headless browser) to automatically fetch fresh m3u8 URLs
More reliable than Selenium and faster
"""

import asyncio
import logging
from playwright.async_api import async_playwright
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StreamURLFetcher:
    """Automatically fetches fresh stream URLs from LiveNOW Fox"""
    
    def __init__(self):
        self.current_url = None
        self.url_expiry = None
        self.page_url = "https://www.livenowfox.com/live"
        
    async def get_fresh_url(self, force_refresh=False):
        """
        Get a fresh stream URL
        Returns cached URL if still valid, otherwise fetches new one
        """
        # Check if we have a valid cached URL
        if not force_refresh and self.current_url and self.url_expiry:
            if datetime.now() < self.url_expiry:
                logger.info("Using cached stream URL (still valid)")
                return self.current_url
        
        logger.info("Fetching fresh stream URL...")
        url = await self._fetch_url_from_page()
        
        if url:
            self.current_url = url
            # URLs typically expire in ~20 minutes, cache for 15 minutes to be safe
            self.url_expiry = datetime.now() + timedelta(minutes=15)
            logger.info(f"Fresh URL obtained, valid until {self.url_expiry}")
        
        return url
    
    async def _fetch_url_from_page(self):
        """Use Playwright to intercept network requests and capture m3u8 URL"""
        try:
            async with async_playwright() as p:
                # Launch browser in headless mode
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                page = await context.new_page()
                
                # Capture m3u8 URLs from network requests
                m3u8_urls = []
                
                async def handle_request(request):
                    url = request.url
                    if '.m3u8' in url and 'manifest.m3u8' in url:
                        if url not in m3u8_urls:  # Avoid duplicates
                            m3u8_urls.append(url)
                            logger.info(f"Captured manifest URL")
                
                page.on('request', handle_request)
                
                # Navigate to the page
                logger.info(f"Loading page: {self.page_url}")
                try:
                    await page.goto(self.page_url, timeout=15000)
                    # Wait just long enough for video request
                    await asyncio.sleep(3)
                except Exception as e:
                    logger.warning(f"Page load warning: {str(e)}")
                
                await browser.close()
                
                # Return the first manifest URL found
                if m3u8_urls:
                    logger.info(f"Successfully captured stream URL")
                    return m3u8_urls[0]
                else:
                    logger.warning("No manifest.m3u8 URL found")
                    return None
                
        except Exception as e:
            logger.error(f"Error fetching URL: {str(e)}")
            return None
    
    def extract_expiry_time(self, url):
        """Extract expiry timestamp from URL if available"""
        try:
            # Look for te= parameter (expiry time)
            match = re.search(r'te=(\d+)', url)
            if match:
                expiry_timestamp = int(match.group(1))
                expiry_time = datetime.fromtimestamp(expiry_timestamp)
                return expiry_time
        except:
            pass
        return None


# Fallback: Use yt-dlp if available
async def get_url_with_ytdlp():
    """Fallback method using yt-dlp"""
    try:
        import subprocess
        result = subprocess.run(
            ['yt-dlp', '-g', '--no-playlist', 'https://www.livenowfox.com/live'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            url = result.stdout.strip().split('\n')[0]
            logger.info("Got URL using yt-dlp")
            return url
    except Exception as e:
        logger.error(f"yt-dlp fallback failed: {str(e)}")
    return None


if __name__ == "__main__":
    # Test the fetcher
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        fetcher = StreamURLFetcher()
        url = await fetcher.get_fresh_url()
        
        if url:
            print("\n" + "="*80)
            print("✓ Successfully fetched stream URL:")
            print(url)
            print("="*80)
            
            # Check expiry
            expiry = fetcher.extract_expiry_time(url)
            if expiry:
                print(f"\nURL expires at: {expiry}")
                remaining = expiry - datetime.now()
                print(f"Time remaining: {remaining}")
        else:
            print("\n✗ Failed to fetch URL")
    
    asyncio.run(test())
