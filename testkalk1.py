from playwright.sync_api import sync_playwright, expect

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(
        "https://ladislavkubini.github.io/python1/Kalkulacka.html"
    )

    page.locator("#cislo-a").fill("12")
    page.locator("#cislo-b").fill("3")
    page.locator("#operacia").select_option("plus")
    page.get_by_role("button", name="Vypočítať", exact=True).click()

    expect(page.locator("#vysledok")).to_have_text("15")
    print("Test sčítania prešiel.")

    browser.close()