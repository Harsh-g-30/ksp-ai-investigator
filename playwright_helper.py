from playwright.sync_api import Page, TimeoutError

TYPE_MAP = {
    "Big Int": "BigInt",
    "Boolean": "Boolean",
    "Date": "Date",
    "Date Time": "DateTime",
    "Decimal": "Decimal",
    "Text": "Text",
    "Var Char(20)": "VarChar",
    "Var Char(30)": "VarChar",
    "Var Char(40)": "VarChar",
    "Var Char(50)": "VarChar",
    "Var Char(60)": "VarChar",
    "Var Char(100)": "VarChar",
    "Var Char(150)": "VarChar",
    "Var Char(200)": "VarChar",
    "Var Char(300)": "VarChar",
}


def wait(page, ms=700):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(ms)


def create_table(page: Page, table_name: str, columns: list):

    print("=" * 70)
    print(f"Creating table : {table_name}")
    print("=" * 70)

    try:

        page.get_by_role("button", name="New Table").click()

        page.get_by_role(
            "textbox",
            name="Table Name",
            exact=True
        ).fill(table_name)

        page.get_by_role("button", name="Create").click()

        wait(page, 1200)

    except Exception as e:
        print(f"Unable to create table {table_name}")
        print(e)
        return

    for col in columns:

        try:

            print(f"   -> {col['name']}")

            page.get_by_role("button", name="New Column").click()

            wait(page, 300)

            row = page.get_by_role(
                "row",
                name="Column Name This field can"
            )

            row.get_by_role("textbox").fill(col["name"])

            wait(page, 200)

            # datatype dropdown
            page.locator(".select2-selection").last.click()

            wait(page, 200)

            page.get_by_role(
                "treeitem",
                name=TYPE_MAP[col["type"]]
            ).click()

            wait(page, 200)

            # VarChar Length
            if col["type"].startswith("Var Char"):

                length = (
                    col["type"]
                    .split("(")[1]
                    .split(")")[0]
                )

                page.get_by_role("spinbutton").fill(length)

            # Mandatory
            if col.get("mandatory"):

                page.locator(".onOffSwt").first.click()

            # Unique
            if col.get("unique"):

                page.locator(
                    "tr:nth-child(13) > td:nth-child(2) > label > .onOffSwt > .onOffBtn"
                ).first.click()

            page.get_by_role("button", name="Create").click()

            wait(page, 700)

        except TimeoutError:

            print(f"Timeout creating column {col['name']}")

        except Exception as e:

            print(f"Failed column : {col['name']}")
            print(e)

    print(f"Finished table {table_name}")