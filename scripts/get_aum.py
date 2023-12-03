import argparse
import csv
import logging
import os
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_data(month):
    """
    Fetches mutual fund data from AMFI website for the specified month.

    :param month : Month and year in the format "Month - Year".
    :returns : The response object from the website.
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


def filename_mapping(quarters_map, year, quarter):
    """
    Storing the mapping for month and filename.

    :param quarters_map : Dict to store the month and filename.
    :param year : Year for which quarter needs to be generated.
    :param quarter : Quarter number for that year.
    """
    start_date = datetime(year, (quarter - 1) * 3 + 1, 1)
    end_date = start_date + timedelta(days=89)
    month = " ".join([start_date.strftime("%B"), "-"])
    month = " ".join([month, end_date.strftime("%B"), str(year)])
    start_date = "-".join(["1", start_date.strftime("%B")])
    start_date = "-".join([start_date, str(year)])
    if quarter in {1, 4}:
        end_date = "-".join(["30", end_date.strftime("%B")])
        end_date = "-".join([end_date, str(year)])
    else:
        end_date = "-".join(["31", end_date.strftime("%B")])
        end_date = "-".join([end_date, str(year)])
    filename = "_".join([start_date, end_date])
    quarters_map[month] = filename


def generate_quarters(
    start_year,
    start_quarter,
    end_year,
    end_quarter,
):
    """
    Generates a mapping of quarters with start and end dates to the filename.

    :param start_year : Start year for fetching data.
    :param start_quarter : Start quarter (1-4) for fetching data.
    :param end_year : End year for fetching data.
    :param end_quarter : End quarter (1-4) for fetching data.
    :returns: A mapping of quarters with start and end dates to the filename.
    """
    quarters_map = {}
    for year in range(start_year, end_year + 1):
        if year == start_year:
            start_quarter_num = start_quarter
        else:
            start_quarter_num = 1
        if year == end_year:
            end_quarter_num = end_quarter
        else:
            end_quarter_num = 4

        for quarter in range(start_quarter_num, end_quarter_num + 1):
            filename_mapping(quarters_map, year, quarter)
    return quarters_map


def skip_rows(rows, index):
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


def get_file_path(rows, index, filename):
    """
    Extracts the folder name from the current row.

    :param rows : List of rows containing mutual fund data.
    :param index : Current index in the rows list.
    :param filename : Name of the file.
    :returns : Folder name.
    """
    folder_name = rows[index].find("th").get_text(strip=True)
    folder_name = folder_name.replace(" ", "")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    filename = ".".join([filename, "csv"])
    return os.path.join(folder_name, filename)


def get_pattern(rows, index):
    """
    Extracts the pattern for the current row.

    :param rows : List of rows containing mutual fund data.
    :param index : Current index in the rows list.
    :returns : Pattern for the current row.
    """
    row = rows[index]
    th_tag = row.find("th")
    return th_tag.get_text(strip=True) if th_tag else " "


def handle_open_ended(rows, index):
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


def get_row_columns(row):
    """
    Extracts the columns for the current row.

    :param row : Current row tag.
    :returns : List of columns for the row.
    """
    cols = row.find_all(["td", "th"])
    return [col.text.strip() for col in cols]


def get_header():
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
        ],
    ]


def generate_csv(rows, filename, index):
    """
    Generates a CSV file for mutual fund data.

    :param rows : List of rows containing mutual fund data.
    :param filename : Filename for the CSV file.
    :param index : Current index in the rows list.
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

            # fetching the columns to add
            csv_writer.writerow(get_row_columns(rows[index]))

            # changing the row to the next
            index = index + 1
            # this line is to be skip row = rows[index]

        index = skip_rows(rows, index)

    return index


def generate_data(month, filename):
    """
    Generates mutual fund data for the specified month and stores it in a CSV file.

    :param month : Month and year in the format "Month - Year".
    :param filename : Filename for the CSV file.
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
                index = generate_csv(rows, filename, index)
    else:
        logger.error(f"Error: {response.status_code}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and store AMFI data.")
    parser.add_argument("--start-year", type=int, help="Start year")
    parser.add_argument("--start-quarter", type=int, help="Start quarter (1-4)")
    parser.add_argument("--end-year", type=int, help="End year")
    parser.add_argument("--end-quarter", type=int, help="End quarter (1-4)")

    args = parser.parse_args()
    if args.start_year and args.start_quarter and args.end_year and args.end_quarter:
        quarters_map = generate_quarters(
            args.start_year,
            args.start_quarter,
            args.end_year,
            args.end_quarter,
        )
        for month, filename in quarters_map.items():
            generate_data(month, filename)
    else:
        logger.error("Please provide valid start and end year and quarter.")
