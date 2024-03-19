import argparse
import csv
import logging
import os
import re
from typing import Dict

import requests  # type: ignore
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def request_amc_codes() -> requests.Response:
    """
    Fetches all the AMC codes from the url and send it.

    :returns : Returns the response
    """
    timeout_seconds = 150
    try:
        url = "https://www.amfiindia.com/nav-history-download"
        response = requests.get(url, timeout=timeout_seconds)
        if response.status_code == 200:
            return response
    except requests.Timeout:
        logger.error("Request timed out. Please try again.")
    except requests.RequestException as excep:
        logger.error(f"An error occurred : {excep}")
        return requests.get(url, timeout=timeout_seconds)


def get_amc_codes() -> Dict[str, str]:
    """
    Fetch AMC codes from the AMFI website.

    :returns : Dictionary of AMC names and their corresponding codes.
    """
    amc_codes: Dict[str, str] = {}
    response = request_amc_codes()
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        logger.info("Request successful")
        soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
        # Extract AMC codes using a regular expression
        for option in soup.find_all("option", {"value": re.compile(r"^\d+$")}):
            amc_codes[option.text] = option["value"]
        return amc_codes
    else:
        logger.error(f"Request failed with code :{response.status_code}")
    return amc_codes


def get_header() -> list[list[str]]:
    """
    Returns the header.

    :returns : returns the static header.
    """
    return [
        [
            "Scheme Code",
            "Scheme Name",
            "ISIN Div Payout/ISIN Growth",
            "ISIN Div Reinvestment",
            "Net Asset Value",
            "Repurchase Price",
            "Sale Price",
            "Date",
        ],
    ]


def get_response(params: dict[str, str]) -> requests.Response:
    """
    Fetches the response from url and sends it.

    :param params : parameters for the get request.
    :returns : returns the response from the url.
    """
    timeout = 150
    base_url = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"
    try:
        response = requests.get(base_url, params=params, timeout=timeout)
        if response.status_code == 200:
            return response
        else:
            logger.error(f"Request failed with code : {response.status_code}")
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after: {timeout}")
    except requests.RequestException as error:
        logger.error(f"Error during request: {error}")
    return response


def fetch_rows(nav_data: str) -> list[list[str]]:
    """
    Return the splitted rows.

    :param nav_data : Data fetched from the url.
    :return : rows
    """
    return [
        row.split(";")
        for row in nav_data.split("\n")
        if row.strip() and len(row.split(";")) > 1
    ]


def generate_csv(rows: list[list[str]], amc_name: str, filename: str) -> None:
    """
    Fetch NAV values for each AMC code and save them to CSV files.

    :param rows : Rows fetched from the url.
    :param amc_name : AMC names.
    :param filename : Filename for the CSV file.
    """
    folder_name = amc_name
    folder_name = folder_name.replace(" ", "")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_path = os.path.join(folder_name, filename)
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(get_header())
        csv_writer.writerows(rows)


def get_params(amc_code: str, start_date: str, end_date: str) -> dict[str, str]:
    """
    Get the parameters for fetching NAV data.

    :param amc_code : The AMC code of the mutual fund.
    :param start_date : The start date of the NAV data.
    :param end_date : The end date of the NAV data.
    :returns : A dictionary containing the parameters for fetching NAV data.
    """
    return {
        "mf": amc_code,
        "frmdt": start_date,
        "todt": end_date,
    }


def process_response(response: requests.Response, amc_name: str, filename: str) -> None:
    """
    Process the response received from the API and generate a CSV file.

    :param response : The response object received from the API.
    :param amc_name : The name of the AMC (Asset Management Company).
    :param filename : The name of the CSV file to be generated.
    """
    tags = {"<html", "<body", "<div", "<p", "<span"}
    if any(tag in response.text.lower() for tag in tags):
        logger.info(f"No data present for {amc_name}")
    else:
        rows = fetch_rows(response.text)[1:]
        generate_csv(rows, amc_name, filename)


def fetch_and_save_nav(
    amc_codes: Dict[str, str],
    start_date: str,
    end_date: str,
    filename: str,
) -> None:
    """
    Fetch NAV values for each AMC code and save them to CSV files.

    :param amc_codes : Dictionary of AMC names and their corresponding codes.
    :param start_date : Start date in the format 'day-month-year'.
    :param end_date : End date in the format 'day-month-year'.
    :param filename : Filename for the CSV file
    """
    filename = ".".join([filename, "csv"])
    for amc_name, amc_code in amc_codes.items():
        response = get_response(get_params(amc_code, start_date, end_date))
        if response.status_code == 200:
            process_response(response, amc_name, filename)
        else:
            logger.error("Error: Unable to fetch NAV values")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch NAV values.")
    parser.add_argument(
        "start_date format dd-mmm-yyyy",
        help='e.g. get_nav.py "11-Feb-2024" "13-Mar-2024"',
    )
    parser.add_argument(
        "end_date format dd-mmm-yyyy",
        help='e.g. get_nav.py "11-Feb-2024" "13-Mar-2024"',
    )
    args = parser.parse_args()
    amc_codes = get_amc_codes()
    if amc_codes:
        filename = "_".join([args.start_date, args.end_date])
        fetch_and_save_nav(amc_codes, args.start_date, args.end_date, filename)
