from playwright.sync_api import sync_playwright


def scrape_website(url):
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

        # Extract text content from the body
        text = page.locator("body").inner_text()

        # Free the RAM
        browser.close()
        return text
