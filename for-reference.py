import asyncio
# import random
# import time
# import csv
from playwright.async_api import async_playwright, expect


async def get_flipkart_product_details(page, url):
    """Scrape product price and discount details from Flipkart."""
    try:
        await page.goto(url)
        price_selector = "#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div:nth-child(2) > div"
        offer_selector = "#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div:nth-child(3)"
        
        await page.wait_for_selector(price_selector, timeout=10000)
        await page.wait_for_selector(offer_selector, timeout=10000)

        # Price
        await page.wait_for_selector(price_selector)
        price_element = page.locator(price_selector)
        
        # Offers
        # Scrape the offer details
        offer_element = page.locator(offer_selector)
        offer = await offer_element.inner_text() if await offer_element.count() > 0 else "Offer not available"

        price = await price_element.inner_text() if await price_element.count() > 0 else "Price not available"
        return {url:url, offer:offer, price:price}

    except Exception as e:
        return {"url": url, "error": f"Flipkart Scraping Error: {str(e)}"}


async def scrape_product(page, url, platform):
    return await get_flipkart_product_details(page, url)


async def scrape_all_products(urls, platform):
    """Scrape all products concurrently."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        tasks = []
        for url in urls:
            tasks.append(scrape_product(page, url, platform))
        
        results = await asyncio.gather(*tasks)

        await browser.close()
        return results



def main():

    flipkart_urls = ["https://www.flipkart.com/oppo-a3-pro-5g-moonlight-purple-256-gb/p/itmc5f69a7aac2a1?pid=MOBHFHC5ZD4FCG9U&lid=LSTMOBHFHC5ZD4FCG9UKR3WKF&marketplace=FLIPKART&fm=neo%2Fmerchandising&iid=M_fb5fa83c-2d76-43c0-99e7-6df9877a28ef_3_ZDI830MIBH_MC.MOBHFHC5ZD4FCG9U&ppt=clp&ppn=plus&ssid=plmwrrfxkw0000001732446128887&otracker=clp_pmu_v2_Oppo%2BMobiles%2Bunder%2B%25E2%2582%25B920K_3_3.productCard.PMU_V2_OPPO%2BA3%2BPro%2B5G%2B%2528Moonlight%2BPurple%252C%2B256%2BGB%2529_oppo-mobile-phones-store_MOBHFHC5ZD4FCG9U_neo%2Fmerchandising_2&otracker1=clp_pmu_v2_PINNED_neo%2Fmerchandising_Oppo%2BMobiles%2Bunder%2B%25E2%2582%25B920K_LIST_productCard_cc_3_NA_view-all&cid=MOBHFHC5ZD4FCG9U"]

    print("Scraping Flipkart Products...")
    flipkart_results = asyncio.run(scrape_all_products(flipkart_urls, platform='flipkart'))
    print(flipkart_results)


if __name__ == "__main__":
    main()
