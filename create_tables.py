from playwright.sync_api import sync_playwright
from schemas import TABLES
from playwright_helper import create_table

CATALYST_URL = "https://console.catalyst.zoho.in/baas/60074366475/index#/"


def main():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=200
        )

        context = browser.new_context(
            viewport={"width": 1600, "height": 900}
        )

        page = context.new_page()

        print("=" * 80)
        print("Opening Catalyst...")
        print("=" * 80)

        page.goto(CATALYST_URL)

        print("\nLogin to Catalyst if required.")
        print("Navigate to:")
        print("Cloud Scale -> Data Store -> Tables")
        print("\nWhen you can see the 'New Table' button, press ENTER.\n")

        input()

        success = []
        failed = []

        # Skip tables already created
        SKIP_TABLES = {
            "State",
            "UnitType",
            "Rank",
            "Designation",
            "CaseCategory",
            "GravityOffence",
            "CaseStatusMaster",
            "CrimeHead",
            "Act",
            "CasteMaster",
            "ReligionMaster",
            "OccupationMaster",
            "District",
            "CrimeSubHead",
            "Section",
        }

        tables_to_create = [
            (name, cols)
            for name, cols in TABLES.items()
            if name not in SKIP_TABLES
        ]

        total = len(tables_to_create)

        print(f"\nStarting creation of {total} tables...\n")

        for index, (table, cols) in enumerate(tables_to_create, start=1):

            print("\n" + "=" * 80)
            print(f"[{index}/{total}] Creating {table}")
            print("=" * 80)

            try:

                create_table(page, table, cols)

                success.append(table)

                print(f"✅ SUCCESS : {table}")

            except Exception as e:

                failed.append((table, str(e)))

                print(f"❌ FAILED : {table}")
                print(e)

        print("\n")
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)

        print(f"Total Remaining Tables : {total}")
        print(f"Successfully Created   : {len(success)}")
        print(f"Failed                 : {len(failed)}")

        if success:

            print("\nSuccessful Tables\n")

            for table in success:
                print(f"✓ {table}")

        if failed:

            print("\nFailed Tables\n")

            for table, err in failed:
                print("-" * 60)
                print(table)
                print(err)

        print("\nAll done!")

        input("\nPress ENTER to close browser...")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()