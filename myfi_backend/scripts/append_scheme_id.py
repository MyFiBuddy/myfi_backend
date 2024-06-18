# flake8: noqa
import csv
from typing import List

import requests  # type: ignore
from bs4 import BeautifulSoup


def get_pattern(rows: List[BeautifulSoup], index: int) -> str:
    """
    Extracts the pattern for the current row.

    :param rows : List of rows containing mutual fund data.
    :param index : Current index in the rows list.
    :returns : Pattern for the current row.
    """
    row = rows[index]
    th_tag = row.find("th")
    return th_tag.get_text(strip=True) if th_tag else " "


def handle_open_ended(rows: List[BeautifulSoup], index: int) -> int:
    """
    Handles the case when the pattern is "Open Ended".

    :param rows : List of rows containing mutual fund data.
    :param index : Current index in the rows list.
    :returns : Updated index.
    """
    index = index + 1
    row = rows[index]
    th_tag = row.find("th")
    return index if th_tag else index + 1


def get_row_columns(row: BeautifulSoup) -> List[str]:
    """
    Extracts the columns for the current row.

    :param row : Current row tag.
    :returns : List of columns for the row.
    """
    cols = row.find_all(["td", "th"])
    return [col.text.strip() for col in cols]


def skip_rows(rows: List[BeautifulSoup], index: int) -> int:
    """
    Skips rows until a condition is met.

    :param rows : List of rows containing mutual fund data.
    :param index : Current index in the rows list.
    :returns : Updated index.
    """
    condition = True
    index = index + 1
    row = rows[index]
    th_tag = row.find("th")

    while index < len(rows) - 1 and condition:
        if th_tag and "align" in th_tag.attrs and th_tag["align"] == "left":
            condition = False
            break
        index += 1
        row = rows[index]
        th_tag = row.find("th")
    return index


def get_header() -> List[List[str]]:
    """
    This function is used for returing header.

    :return : returns the header for NAV
    """
    return [
        [
            "AMFI Code ",
            "Scheme NAV Name",
            "Average AUM - Funds-Overseas",
            "Average AUM-Fund Of Funds - Domestic",
            "Temperory",
        ],
    ]


if __name__ == "__main__":
    """
    Script can be run directly python this_script_name.py
    Performance.py should be run prior to this script
    """
    url = "https://www.amfiindia.com/modules/AverageAUMDetails"
    data = {
        "AUmType": "S",
        "AumCatType": "Typewise",
        "MF_Id": "-1",
        "Year_Id": "0",
        "Year_Quarter": "January - March 2024",
    }
    # Fetching the data from amfi site and storing it in mutual_fund.csv
    response = requests.post(url, data=data)
    print(response)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.select_one("table")
    if table:
        rows = table.find_all("tr")
        index = 4
        filename = "Mutual_Fund.csv"
        with open(filename, "w", newline="", encoding="utf-8") as fd:
            csv_writer = csv.writer(fd)
            csv_writer.writerows(get_header())
            while index < len(rows) - 1:
                pattern = get_pattern(rows, index)
                if pattern in {"Mutual Fund Total", "Interval Fund", "Close Ended"}:
                    index = skip_rows(rows, index)
                    index = index + 1
                    continue

                if pattern == "Open Ended":
                    index = handle_open_ended(rows, index)
                    continue

                # fetching the columns to add
                csv_writer.writerow(get_row_columns(rows[index]))

                # changing the row to the next
                index = index + 1

    """
    scheme_data_22_may-2024.csv file is generated from the get_performance which will get us all the data
    except the scheme id, so scheme and scheme_id we will get after running this script.
    Appending scheme ID to the prev data that we got from get_performance and result is saved inside modified.csv

    SchemeID is appended only after string matching, We compare the name in both AMFI website and output of performace.py script


    """
    Scheme_Type_Growth = "Growth"
    Scheme_Type_Bonus = "Bonus"
    Scheme_Type_Direct = "Direct"
    Scheme_Type_Regular = "Regular"
    with open("output.txt", "a") as file:
        with open("scheme_data_22-May-2024.csv", "r") as input_file:
            csvreader = csv.reader(input_file)
            with open(
                "scheme_data_22-May-2024_modified.csv",
                "w",
                newline="",
            ) as output_file:
                #         # Create a CSV writer object
                csvwriter = csv.writer(output_file)
                for row in csvreader:
                    Scheme_name_Custom = row[0]
                    Scheme_name_Custom = Scheme_name_Custom.lower()
                    Scheme_Type = row[5]
                    with open("Mutual_Fund.csv", "r") as input_file2:
                        column = 1
                        csvreader2 = csv.reader(input_file2)
                        Regular_Scheme_Code = 0
                        Direct_Scheme_Code = 0
                        Regular_Scheme_Code_Real = 0
                        Written = 0
                        Flag = 0
                        found = 0
                        for row2 in csvreader2:
                            if len(row2) > column:
                                Scheme_name_AMFI = row2[column]
                                Scheme_name_AMFI = Scheme_name_AMFI.lower()
                                """
                                Checking if growth exist in sctring
                                And then checking if bous keyword is there, if bonus is there we will skip it.
                                we only check growth keyword and then "Regular" or "Direct" keyword
                                """
                                if Scheme_Type_Growth in Scheme_name_AMFI:
                                    if Scheme_Type_Bonus in Scheme_name_AMFI:
                                        continue
                                    else:
                                        if Scheme_name_Custom in Scheme_name_AMFI:
                                            if (
                                                Scheme_Type == Scheme_Type_Direct
                                                and Scheme_Type_Direct
                                                in Scheme_name_AMFI
                                            ):
                                                file.write(
                                                    "Matched AMFI direct schme "
                                                    + Scheme_name_AMFI
                                                    + " with Custom "
                                                    + Scheme_name_Custom,
                                                )
                                                Direct_Scheme_Code = int(row2[0])
                                                row[1] = str(Direct_Scheme_Code)
                                                csvwriter.writerow(row)
                                                found = found + 1
                                            if (
                                                Scheme_Type == Scheme_Type_Regular
                                                and Scheme_Type_Direct
                                                not in Scheme_name_AMFI
                                            ):
                                                file.write(
                                                    "Matched AMFI Regular scheme "
                                                    + Scheme_name_AMFI
                                                    + " with Custom "
                                                    + Scheme_name_Custom,
                                                )
                                                if (
                                                    Scheme_Type_Regular
                                                    in Scheme_name_AMFI
                                                    and Written == 0
                                                ):
                                                    Regular_Scheme_Code_Real = int(
                                                        row2[0],
                                                    )
                                                    row[1] = str(
                                                        Regular_Scheme_Code_Real,
                                                    )
                                                    csvwriter.writerow(row)
                                                    found = found + 1
                                                    Flag = 1
                                                    if Written == 1:
                                                        Written = 0
                                                if (
                                                    Regular_Scheme_Code == 0
                                                    and Flag == 0
                                                ):
                                                    Regular_Scheme_Code = int(row2[0])
                                                    Written = 1
                        if Written == 1:
                            row[1] = str(Regular_Scheme_Code)
                            csvwriter.writerow(row)
