from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)


def ensure_full_url(url):
    """Ensure the URL starts with http:// or https://"""
    if not url.startswith(('http://', 'https://')):
        return f"https://{url.lstrip('//')}"
    return url


async def get_flipkart_product_details(url):
    """Scrape product price and discount details from Flipkart."""
    url = ensure_full_url(url)  # Fix incomplete URLs
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=30000)  # Adjust timeout as needed
            
            # Selectors
            price_selector = "#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div:nth-child(2) > div"
            offer_selector = "#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div:nth-child(3)"
            
            await page.wait_for_selector(price_selector, timeout=10000)
            await page.wait_for_selector(offer_selector, timeout=10000)

            # Price
            price_element = page.locator(price_selector)
            price = await price_element.inner_text() if await price_element.count() > 0 else "Price not available"
            
            # Offers
            offer_element = page.locator(offer_selector)
            offer = await offer_element.inner_text() if await offer_element.count() > 0 else "Offer not available"
            
            return {"url": url, "price": price, "offer": offer}

        except Exception as e:
            return {"url": url, "error": f"Error scraping Flipkart: {str(e)}"}
        finally:
            await browser.close()



@app.route('/scrape', methods=['POST'])
def scrape():
    """Endpoint to scrape Flipkart product details."""
    data = request.get_json()
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    # Scrape all URLs asynchronously
    async def scrape_all():
        tasks = [get_flipkart_product_details(url) for url in urls]
        return await asyncio.gather(*tasks)

    results = asyncio.run(scrape_all())
    return jsonify(results)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)

