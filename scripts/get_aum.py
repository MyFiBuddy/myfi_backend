import argparse
import csv
import os
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup


def get_data(month):
    """
    Fetches Average AUM data from the AMFI website for a given month.

    Parameters:
        month (str): Month and year in the format "Month - Year"
        (e.g., "January - March 2022").

    Returns:
        requests.Response: The response object from the website.
    """
    url = "https://www.amfiindia.com/modules/AverageAUMDetails"
    data = {
        "AUmType": "S",
        "AumCatType": "Typewise",
        "MF_Id": "-1",
        "Year_Id": "0",
        "Year_Quarter": month,
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error during request: {e}")
    return response


def generate_quarters(start_year, start_quarter, end_year, end_quarter):
    """
    Generates a mapping of quarters with start and end dates based on input parameters.

    Parameters:
        start_year (int): Start year for fetching data.
        start_quarter (int): Start quarter (1-4) for fetching data. (1->January - March)
        end_year (int): End year for fetching data.
        end_quarter (int): End quarter (1-4) for fetching data.

    Returns:
        dict: A mapping of quarters with start and end dates to the filename.
    """
    quarters_mapping = {}

    for year in range(start_year, end_year + 1):
        start_quarter_num = 1 if year != start_year else start_quarter
        end_quarter_num = 4 if year != end_year else end_quarter

        for quarter in range(start_quarter_num, end_quarter_num + 1):
            start_date = datetime(year, (quarter - 1) * 3 + 1, 1)
            end_date = start_date + timedelta(days=89)
            month = (
                start_date.strftime("%B")
                + " "
                + "-"
                + " "
                + end_date.strftime("%B")
                + " "
                + str(year)
            )
            start_date = "1" + "-" + start_date.strftime("%B") + "-" + str(year)
            if quarter == 1 or quarter == 4:
                end_date = "31" + "-" + end_date.strftime("%B") + "-" + str(year)
            else:
                end_date = "30" + "-" + end_date.strftime("%B") + "-" + str(year)
            quarters_mapping[month] = start_date + "_" + end_date

    return quarters_mapping


def Skip_rows(rows, index, length):
    """
    Skips rows until a condition is met.

    Parameters:
        rows (list): List of rows containing mutual fund data.
        index (int): Current index in the rows list.
        length (int): Length of the rows list.

    Returns:
        int: Updated index.
    """
    condition = True
    index = index + 1
    row = rows[index]
    th_tag = row.find("th")

    while index < length - 1 and condition:
        if th_tag and "align" in th_tag.attrs and th_tag["align"] == "left":
            condition = False
            break
        index += 1
        row = rows[index]
        th_tag = row.find("th")
    return index


def get_folder_name(rows, index):
    """
    Gets the folder name for the CSV file.

    Parameters:
        rows (list): List of rows containing mutual fund data.
        index (int): Current index in the rows list.

    Returns:
        str: Folder name.
    """
    folder_name = rows[index].find("th").get_text(strip=True)
    return folder_name.replace(" ", "")


def get_pattern(rows, index):
    """
    Gets the pattern for the current row.

    Parameters:
        rows (list): List of rows containing mutual fund data.
        index (int): Current index in the rows list.

    Returns:
        str: Pattern for the current row.
    """
    row = rows[index]
    th_tag = row.find("th")
    return th_tag.get_text(strip=True) if th_tag else " "


def handle_open_ended(rows, index):
    """
    Handles the case when the pattern is "Open Ended".

    Parameters:
        rows (list): List of rows containing mutual fund data.
        index (int): Current index in the rows list.

    Returns:
        int: Updated index.
    """
    index = index + 1
    row = rows[index]
    th_tag = row.find("th")
    return index if th_tag else index + 1


def get_row_columns(row):
    """
    Gets the columns for the current row.

    Parameters:
        row (BeautifulSoup Tag): Current row tag.

    Returns:
        list: List of columns for the row.
    """
    cols = row.find_all(["td", "th"])
    return [col.text.strip() for col in cols]


def generate_csv(rows, filename, index, length):
    """
    Generates CSV files with the extracted data for each mutual fund scheme.

    Parameters:
        rows (list): List of rows containing mutual fund data.
        filename (str): Filename for the CSV file.
        index (int): Current index in the rows list.
        length (int): Length of the rows list.

    Returns:
        int: Updated index after processing the rows.
    """
    Headers = [
        [
            "AMFI Code ",
            "Scheme NAV Name",
            "Average AUM-Excluding Fund of Funds - Domestic but including Fund of \
          Funds - Overseas",
            "Average AUM-Fund Of Funds - Domestic",
        ],
    ]
    folder_name = get_folder_name(rows, index)
    filename = filename + "." + "csv"
    file_path = os.path.join(folder_name, filename)
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(Headers)
        index = index + 1
        while index < length - 1:
            pattern = get_pattern(rows, index)
            row = rows[index]
            if pattern in {"Mutual Fund Total", "Interval Fund", "Close Ended"}:
                break

            if pattern == "Open Ended":
                index = handle_open_ended(rows, index)
                continue

            cols = get_row_columns(row)
            csv_writer.writerow(cols)

            # changing the row to the next
            index = index + 1
            row = rows[index]

        index = Skip_rows(rows, index, length)

    return index


def generate_data(month, filename):
    """
    Fetches and processes data for a specific month and generates CSV files.
    Parameters:
        month (str): Month and year in the format "Month - Year"
        (e.g., "January - March 2022").
        filename (str): Filename for the CSV file.
    """
    response = get_data(month)
    if response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.select_one("table")
        if table:
            rows = table.find_all("tr")
            length = len(rows)
            index = 4
            # Iterating until "Close Ended" string is not encountered.
            while index < length - 1:
                index = generate_csv(rows, filename, index, length)

    else:
        print(f"Error: {response.status_code}")


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
        print("Please provide valid start and end year and quarter.")
