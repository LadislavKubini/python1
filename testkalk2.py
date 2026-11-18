from playwright.sync_api import sync_playwright, expect

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    def vymazat():
        page.get_by_role(
            "button", name="Vymazať", exact=True
        ).click()

        # Overenie, že sa formulár vymazal.
        expect(page.locator("#cislo-a")).to_have_value("")
        expect(page.locator("#cislo-b")).to_have_value("")
        expect(page.locator("#operacia")).to_have_value("plus")
        expect(page.locator("#vysledok")).to_have_text("")
        expect(page.locator("#chyba")).to_have_text("")

    def doCalc(cislo1, operator, cislo2, expResult):
        vymazat()

        # Symbol operácie prevedieme na hodnotu v HTML selecte.
        operacie = {
            "+": "plus",
            "-": "minus",
            "*": "krat",
            "/": "deleno",
        }

        page.locator("#cislo-a").fill(str(cislo1))
        page.locator("#cislo-b").fill(str(cislo2))
        page.locator("#operacia").select_option(operacie[operator])

        page.get_by_role(
            "button", name="Vypočítať", exact=True
        ).click()

        # Počkáme na vyplnenie výsledku.
        expect(page.locator("#vysledok")).not_to_have_text("")

        # Najprv získame text, potom ho porovnáme.
        skutocny_vysledok = page.locator("#vysledok").inner_text()
        ocakavany_vysledok = str(expResult)

        uspesny = skutocny_vysledok == ocakavany_vysledok
        vypocet = f"{cislo1} {operator} {cislo2} = {skutocny_vysledok}"

        if uspesny:
            print(f"OK     {vypocet}")
        else:
            print(
                f"CHYBA  {vypocet}"
                f"   očakávané: {ocakavany_vysledok}"
            )

        return uspesny

    try:
        page.goto(
            "https://ladislavkubini.github.io/python1/Kalkulacka.html"
        )

        vysledky = []
        vysledky.append(doCalc(12, "+", 3, "15"))
        vymazat()
        vysledky.append(doCalc(12, "-", 20, "-8"))
        vymazat()
        vysledky.append(doCalc(-4, "*", 3, "-12"))
        vymazat()
        vysledky.append(doCalc(7, "/", 3, "3.5"))
        vymazat()        

        print()
        print(f"Úspešné testy: {sum(vysledky)} / {len(vysledky)}") # bool sa pocita ako 0 / 1

    finally:
        browser.close()