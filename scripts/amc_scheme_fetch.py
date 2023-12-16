import csv
import logging
import os
from datetime import datetime
from typing import List

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_data(month: str) -> requests.Response:
    """
    Fetches mutual fund data from AMFI website for the specified month.

    :param month: Month and year in the format "Month - Year".
    :returns: The response object from the website.
    """
    url = "https://www.amfiindia.com/modules/AverageAUMDetails"
    data = {
        "AUmType": "S",
        "AumCatType": "Typewise",
        "MF_Id": "-1",
        "Year_Id": "0",
        "Year_Quarter": month,
    }
    timeout_seconds = 150
    try:
        response = requests.post(url, data=data, timeout=timeout_seconds)
        if response.status_code == 200:
            return response
        else:
            logger.error(f"Request failed with code: {response.status_code} ")
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after : {timeout_seconds} ")
    except requests.RequestException as error:
        logger.error(f"Error during request : {error}")
    return response


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


def get_file_path(rows: List[BeautifulSoup], index: int, filename: str) -> str:
    """
    Extracts the folder name from the current row.

    :param rows : List of rows containing mutual fund data.
    :param index : Current index in the rows list.
    :param filename : Name of the file.
    :returns : Folder name.
    """
    th_tag = rows[index].find("th")
    folder_name = th_tag.get_text(strip=True) if th_tag is not None else ""
    folder_name = folder_name.replace(" ", "")
    if folder_name and not os.path.exists(folder_name):
        os.makedirs(folder_name)
    filename = ".".join([filename, "csv"])
    return os.path.join(folder_name, filename)


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


def get_row_columns(rows: List[BeautifulSoup], index: int) -> List[str]:
    """
    Extracts the columns for the current row.

    :param rows : rows data.
    :param index : Current index in the rows list.
    :returns : List of columns for the row.
    """
    row = rows[index]
    cols = row.find_all(["td", "th"])
    cols = cols[:-2]  # Remove the last two elements
    return [col.text.strip() for col in cols]


def get_header() -> List[List[str]]:
    """
    This function is used for returing header.

    :return : returns the header for NAV
    """
    return [
        [
            "AMC Name",
            "Scheme Code ",
            "Scheme Name",
            "Distributor Type",
            "Growth Type",
        ],
    ]


def get_amc(rows, index) -> str:
    """
    Extracts the AMC name from the current row.

    :param rows : List of rows containing mutual fund data.
    :param index : Current index in the rows list.
    :returns : AMC name.
    """
    th_tag = rows[index].find("th")
    amc_name = th_tag.get_text(strip=True) if th_tag is not None else ""
    return amc_name.replace(" ", "")


def parse_amc_scheme_name(pattern: str, scheme_name: str) -> bool:
    """
    Checks if the pattern is present in the schemes name of the AMC.

    :param pattern : List of schemes for the AMC.
    :param scheme_name : Name of the scheme.
    :returns : Returns True if pattern matches else False.
    """
    if pattern in scheme_name.lower():
        return True
    return False


def append_list(rows: List[BeautifulSoup], index: int, amc_name: str) -> List[str]:
    """
    Extracts the columns for the current row.

    :param rows : rows data.
    :param index : Current index in the rows list.
    :param amc_name : AMC name.
    :returns : List of columns for the row.
    """
    row_data = get_row_columns(rows, index)
    row_data = [amc_name] + row_data
    if parse_amc_scheme_name("direct", row_data[2]):
        row_data.append("Direct")
    elif parse_amc_scheme_name("regular", row_data[2]):
        row_data.append("Regular")
    else:
        row_data.append("")
    if parse_amc_scheme_name("growth", row_data[2]):
        row_data.append("Growth")
    elif parse_amc_scheme_name("idcw", row_data[2]):
        row_data.append("Divident")
    elif parse_amc_scheme_name("dividend", row_data[2]):
        row_data.append("Divident")
    else:
        row_data.append("")
    return row_data


def generate_csv(
    rows: List[BeautifulSoup],
    filename: str,
    index: int,
    amc_name: str,
) -> int:
    """
    Generates a CSV file for mutual fund data.

    :param rows : List of rows containing mutual fund data.
    :param filename : Filename for the CSV file.
    :param index : Current index in the rows list.
    :param amc_name : AMC name.
    :return : Updated index after processing the rows.
    """
    filename = get_file_path(rows, index, filename)
    with open(filename, "w", newline="", encoding="utf-8") as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerows(get_header())
        index = index + 1
        while index < len(rows) - 1:
            pattern = get_pattern(rows, index)
            if pattern in {"Mutual Fund Total", "Interval Fund", "Close Ended"}:
                break

            if pattern == "Open Ended":
                index = handle_open_ended(rows, index)
                continue
            csv_writer.writerow(append_list(rows, index, amc_name))
            # changing the row to the next
            index = index + 1
            # this line is to be skip row = rows[index]

        index = skip_rows(rows, index)

    return index


def generate_data(month: str, fname: str) -> None:
    """
    Generates mutual fund data for the specified month and stores it in a CSV file.

    :param month : Month and year in the format "Month - Year".
    :param fname : Filename for the CSV file.
    """
    response = get_data(month)
    if response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.select_one("table")
        if table:
            rows = table.find_all("tr")
            index = 4
            # Iterating until "Close Ended" string is not encountered.
            while index < len(rows) - 1:
                index = generate_csv(rows, fname, index, get_amc(rows, index))
    else:
        logger.error(f"Error: {response.status_code}")


def get_latest_quarter() -> str:
    """
    This function is used for getting the latest quarter.

    :return : returns the latest quarter
    """
    # Get the current date
    current_date = datetime.now()
    # Get the current year
    current_year = current_date.year

    # Determine the quarter
    if 1 <= current_date.month < 4:
        latest_quarter = " ".join(["october - december", str(current_year - 1)])
    elif 4 <= current_date.month < 7:
        latest_quarter = " ".join(["january - march", str(current_year)])
    elif 7 <= current_date.month < 10:
        latest_quarter = " ".join(["april - june", str(current_year)])
    else:
        latest_quarter = " ".join(["july - september", str(current_year)])

    return latest_quarter


if __name__ == "__main__":
    latest_quarter = get_latest_quarter()
    generate_data(latest_quarter, latest_quarter)
