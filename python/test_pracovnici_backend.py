from playwright.sync_api import sync_playwright, expect
import json

BASE_URL = "http://127.0.0.1:8000"
PAGE_URL = f"{BASE_URL}/Pracovnici.html"
API_URL = f"{BASE_URL}/api/pracovnici.php"

def obnov_testovacie_udaje(page):
    button = page.get_by_role(
        "button",
        name="Obnoviť testovacie údaje"
    )
    button.click()

    # Tlačidlo sa počas obnovy zakáže a po dokončení znovu povolí.
    expect(button).to_be_enabled(timeout=30000)

def skontroluj_json(response, ocakavany_status):
    assert response.status == ocakavany_status, (
        f"Očakávaný HTTP {ocakavany_status}, "
        f"dostal som HTTP {response.status}"
    )

    content_type = response.headers.get("content-type", "").lower()
    assert "application/json" in content_type, (
        f"Očakávaný JSON, Content-Type je {content_type!r}"
    )

    return response.json()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Príprava databázy cez existujúce tlačidlo stránky.
        page.goto(PAGE_URL)
        obnov_testovacie_udaje(page)
        print("Obnova pôvodných údajov: OK")

        # GET pred zmenami: počet záznamov a nezmenený pracovník ID 4.
        response = context.request.get(API_URL)
        udaje = skontroluj_json(response, 200)

        assert len(udaje) == 5, f"Očakávaných 5 záznamov, prišlo {len(udaje)}"

        podla_id = {zaznam["id"]: zaznam for zaznam in udaje}
        assert podla_id[4] == {
            "id": 4,
            "meno": "Ján Horváth",
            "oddelenie": "Výroba",
            "aktivny": True,
        }

        print("GET pred zmenami: OK")

        # Každý PUT mení jeden existujúci záznam.
        ocakavane = [
            {
                "id": 2,
                "meno": "Anton Kováč",
                "oddelenie": "Účtovníctvo",
                "aktivny": False,
            },
            {
                "id": 1,
                "meno": "Anna Nováková",
                "oddelenie": "Výroba",
                "aktivny": True,
            },
            {
                "id": 3,
                "meno": "Iveta Mauréry",
                "oddelenie": "IT",
                "aktivny": True,
            },
            {
                "id": 5,
                "meno": "Eva Bieliková",
                "oddelenie": "IT",
                "aktivny": False,
            },
        ]

        for pracovnik in ocakavane:
            response = context.request.put(
                API_URL,
                data=json.dumps(pracovnik, ensure_ascii=False),
                headers={"Content-Type": "application/json"},
            )

            vysledok = skontroluj_json(response, 200)
            assert vysledok == pracovnik, (
                f"Nesprávna odpoveď PUT pre ID {pracovnik['id']}: {vysledok}"
            )

        print("PUT pre ID 1, 2, 3 a 5: OK")

        # GET po zmenách: porovnanie JSON objektov, nezávislé od ich formátovania
        # alebo poradia kľúčov.
        response = context.request.get(API_URL)
        udaje = skontroluj_json(response, 200)

        assert len(udaje) == 5, f"Očakávaných 5 záznamov, prišlo {len(udaje)}"

        skutocne = {zaznam["id"]: zaznam for zaznam in udaje}
        ocakavane_vsetky = {
            pracovnik["id"]: pracovnik for pracovnik in ocakavane
        }
        ocakavane_vsetky[4] = {
            "id": 4,
            "meno": "Ján Horváth",
            "oddelenie": "Výroba",
            "aktivny": True,
        }

        assert skutocne == ocakavane_vsetky, (
            f"Výsledné údaje sa nezhodujú.\n"
            f"Očakávané: {ocakavane_vsetky}\n"
            f"Skutočné:  {skutocne}"
        )

        print("GET po zmenách a kontrola všetkých 5 záznamov: OK")

    finally:
        # Obnoviť pôvodné údaje aj po zlyhaní niektorého testu.
        try:
            obnov_testovacie_udaje(page)
            print("Obnovenie pôvodných údajov po teste: OK")
        except Exception as chyba:
            print(f"POZOR: Obnova údajov po teste zlyhala: {chyba}")

        browser.close()