from playwright.sync_api import sync_playwright


def scrape_anchors(url):
    print("Verifying Playwright browser path...")

    with sync_playwright() as p:
        print(p.chromium.executable_path)

        # Launch the browser
        browser = p.chromium.launch(
            executable_path="/root/.cache/ms-playwright/chromium-1148/chrome-linux/chrome",
            headless=True
        )
        page = browser.new_page()
        page.goto(url)

        # Extract all anchor tags with href containing 2024 or 2025
        anchors = page.locator("a[href*='2024'], a[href*='2025']")
        hrefs = anchors.evaluate_all(
            "elements => elements.map(el => ({ href: el.href, text: el.textContent.trim() }))")
        print(hrefs)
        # Free the RAM
        browser.close()
        return hrefs


def scrape_website(url):
    print("Verifying Playwright browser path...")

    with sync_playwright() as p:
        print(p.chromium.executable_path)
        print("Trying to scrape...")

        # Launch the browser
        browser = p.chromium.launch(
            executable_path="/root/.cache/ms-playwright/chromium-1148/chrome-linux/chrome",
            headless=True
        )
        page = browser.new_page()
        page.goto(url)

        text = ""
        # Extract text content from the body
        try:
            text = page.locator("#main-content").inner_text()
            print("Scraped successfully!")
        except Exception as e:
            print(f"Failed to scrape content: {e}")
            text = page.locator("body").inner_text()
            print("Scraped successfully!")

        # Free the RAM
        browser.close()
        print("Scraped successfully!")
        return text
