import asyncio
import random
import time
import csv
from playwright.async_api import async_playwright, expect

async def get_amazon_product_details(page, url):
    """Scrape product price and discount details from Amazon."""
    try:
        await page.goto(url)
        price_selector = "#corePriceDisplay_desktop_feature_div > div.a-section.a-spacing-none.aok-align-center.aok-relative"
        
        # Wait for the price element to load
        await page.wait_for_selector(price_selector)
        
        price_element = page.locator(price_selector)
        price = await price_element.inner_text() if await price_element.count() > 0 else "Price not available"
        return price
    except Exception as e:
        return f"Amazon Scraping Error: {str(e)}"

async def get_flipkart_product_details(page, url):
    """Scrape product price and discount details from Flipkart."""
    try:
        await page.goto(url)
        price_selector = "#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div:nth-child(2) > div"
        
        # Wait for the price element to load
        await page.wait_for_selector(price_selector)
        
        price_element = page.locator(price_selector)
        price = await price_element.inner_text() if await price_element.count() > 0 else "Price not available"
        return price
    except Exception as e:
        return f"Flipkart Scraping Error: {str(e)}"

# Add more functions for other platforms (Croma, Reliance Digital) if necessary
async def get_croma_product_details(page, url):
    """Scrape product price and discount details from Croma."""
    try:
        await page.goto(url)
        # Example price selector for Croma (adjust as per actual structure)
        price_selector = "#pdpdatael > div.cp-section.banner-spacing.show-pdp-icon > div.container > div > div > div > div.col-md-6.right-alignElement > div > ul > li.info-item.item-space-reduce"
        await page.wait_for_selector(price_selector)
        price_element = page.locator(price_selector)
        price = await price_element.inner_text() if await price_element.count() > 0 else "Price not available"
        return price
    except Exception as e:
        return f"Croma Scraping Error: {str(e)}"

async def get_reliance_digital_product_details(page, url):
    """Scrape product price and discount details from Reliance Digital."""
    try:
        await page.goto(url)
        # Example price selector for Reliance Digital (adjust as per actual structure)
        price_selector = "#root > main > div.pb__20 > div > section.pdpStickyContainer > div.blk__sm__7.flush__left.pdp__topBlock > div:nth-child(2) > div.TextWeb__Text-sc-1cyx778-0.cXyRgU.Block-sc-u1lygz-0.gzqHuV.blk__sm__5.flush__left.flush__right.hideOverFlow.mt__16 > div.TextWeb__Text-sc-1cyx778-0.cXyRgU.Block-sc-u1lygz-0.gFTZAm > ul"
        await page.wait_for_selector(price_selector)
        price_element = page.locator(price_selector)
        price = await price_element.inner_text() if await price_element.count() > 0 else "Price not available"
        return price
    except Exception as e:
        return f"Reliance Digital Scraping Error: {str(e)}"

async def scrape_product(page, device_name, url, platform):
    """Scrape product details based on platform and return device name along with details."""
    if platform == 'amazon':
        price = await get_amazon_product_details(page, url)
    elif platform == 'flipkart':
        price = await get_flipkart_product_details(page, url)
    elif platform == 'croma':
        price = await get_croma_product_details(page, url)
    elif platform == 'reliance_digital':
        price = await get_reliance_digital_product_details(page, url)
    else:
        price = "Platform not supported"
    
    return {
        "device_name": device_name,
        "platform": platform,
        "url": url,
        "price": price
    }

async def scrape_all_products(devices_urls):
    """Scrape all products concurrently for multiple platforms."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        tasks = []
        for device_name, urls in devices_urls.items():
            for url in urls:
                # Extract platform name from the URL (based on domain)
                if "amazon" in url:
                    platform = "amazon"
                elif "flipkart" in url:
                    platform = "flipkart"
                elif "croma" in url:
                    platform = "croma"
                elif "reliancedigital" in url:
                    platform = "reliance_digital"
                else:
                    platform = "unknown"

                tasks.append(scrape_product(page, device_name, url, platform))
        
        results = await asyncio.gather(*tasks)
        
        await browser.close()
        return results

def save_results_to_csv(results, output_file="scraped_product_details.csv"):
    """Save the scraped product details to a CSV file."""
    keys = results[0].keys()
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

def main():
    # Dictionary of devices with platform URLs
    devices_urls = {
        "Samsung Galaxy S23": [
            "https://www.amazon.in/Samsung-Galaxy-Cream-256GB-Storage/dp/B0BTYVTMT6/ref=sr_1_5?crid=3SVOLZ8U1LQG7&dib=eyJ2IjoiMSJ9.a0buvK5PjoR0OZT_PeGDsP851aZcopk63HlDnv9m6DXFCJYWfxgl7neqNctU-gPi_aIO2cR1_F7IjeEr75vdMKQl14phrXgUsE53Ispfg0RUjy-x4EU9AVCmjUyOAxfLUOoISd2TO--CzeRzj5uOu3urOclwlPQ3eqWt7lx_LHc7RoGyTZNAtIPZYTv9nMhsnjfTIXiUKXo4RkRmM_CrIup5FXhvfA4fPpdU3VmWdLk6Z3aLCYQkMF9ek1Babb2R8sPOGmyh5sxy0Da5iVvlWHRKN9ZyJoNUhK-FTcqfrCA.eSc5yHKUVWDo9r0Wt4MDSERhYwONzLff9LmCV83gtuM&dib_tag=se&keywords=Samsung+Galaxy+S23&nsdOptOutParam=true&qid=1732218258&s=electronics&sprefix=%2Celectronics%2C250&sr=1-5",  # Amazon URL
            "https://www.flipkart.com/samsung-galaxy-s23-5g-cream-128-gb/p/itmc77ff94cdf044?pid=MOBGMFFX5XYE8MZN&lid=LSTMOBGMFFX5XYE8MZNRGKCA5&marketplace=FLIPKART&q=Samsung+Galaxy+S23&store=tyy%2F4io&srno=s_1_1&otracker=search&otracker1=search&fm=organic&iid=en_dDxPgxKpKQIUfhEvJMo0XZBQnpV1-yugoXovwHtuOqgYjhtRNgQpkRm1ITrex2hzYuWjhJDg2kStSrXFEoo_rw%3D%3D&ppt=pp&ppn=pp&ssid=2l4mm1c18g0000001732218264883&qH=1fe033b290fff2a3",  # Flipkart URL
            "https://www.croma.com/samsung-galaxy-s23-5g-8gb-ram-128gb-cream-/p/268869",  # Croma URL (Example)
            "https://www.reliancedigital.in/samsung-galaxy-s23-5g-128-gb-8-gb-ram-lavender-mobile-phone/p/493665066"  # Reliance Digital URL (Example)
        ]
        # "Apple iPhone 15": [
        #     "https://www.amazon.in/Apple-iPhone-15/dp/B0YYYY",  # Amazon URL
        #     "https://www.flipkart.com/apple-iphone-15/p/itmYYYY",  # Flipkart URL
        #     # Other platform URLs if needed
        # ]
    }

    # Scrape product details from all platforms
    print("Scraping product details from multiple platforms...")
    results = asyncio.run(scrape_all_products(devices_urls))

    # Save results to CSV
    save_results_to_csv(results)
    print(f"Scraped details for {len(results)} products. Results saved to 'scraped_product_details.csv'.")

if __name__ == "__main__":
    main()
