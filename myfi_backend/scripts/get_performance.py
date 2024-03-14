"""
This script gets the performance data of mutual funds via API.

It fetches the data for all the primary categories and their respective categories.
The performance data of schemes is then written to a CSV file.
"""

import csv
import logging
import os
import tempfile
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import httpx
import xlrd

# Define mutual fund map
mutual_fund_map = {
    "9636": "360 ONE Mutual Fund",
    "4": "Aditya Birla Sun Life Mutual Fund",
    "8799": "Axis Mutual Fund",
    "20129": "Bajaj Finserv Mutual Fund",
    "298": "Bandhan Mutual Fund",
    "332": "Bank of India Mutual Fund",
    "312": "Baroda BNP Paribas Mutual Fund",
    "8": "Canara Robeco Mutual Fund",
    "181": "DSP Mutual Fund",
    "339": "Edelweiss Mutual Fund",
    "28": "Franklin Templeton Mutual Fund",
    "9655": "Groww Mutual Fund",
    "302": "HDFC Mutual Fund",
    "20217": "Helios Mutual Fund",
    "308": "HSBC Mutual Fund",
    "14": "ICICI Prudential Mutual Fund",
    "319": "Invesco Mutual Fund",
    "12232": "ITI Mutual Fund",
    "19": "JM Financial Mutual Fund",
    "218": "Kotak Mahindra Mutual Fund",
    "21": "LIC Mutual Fund",
    "11141": "Mahindra Manulife Mutual Fund",
    "327": "Mirae Asset Mutual Fund",
    "9054": "Motilal Oswal Mutual Fund",
    "8927": "Navi Mutual Fund",
    "24": "Nippon India Mutual Fund",
    "12931": "NJ Mutual Fund",
    "20419": "Old Bridge Mutual Fund",
    "9055": "PGIM India Mutual Fund",
    "10157": "PPFAS Mutual Fund",
    "11": "Quant Mutual Fund",
    "317": "Quantum Mutual Fund",
    "13005": "Samco Mutual Fund",
    "25": "SBI Mutual Fund",
    "26": "Shriram Mutual Fund",
    "187": "Sundaram Mutual Fund",
    "27": "Tata Mutual Fund",
    "10": "Taurus Mutual Fund",
    "12751": "TRUST Mutual Fund",
    "9521": "Union Mutual Fund",
    "311": "UTI Mutual Fund",
    "12160": "WhiteOak Capital Mutual Fund",
    "20245": "Zerodha Mutual Fund",
}

# Define primary categories and their respective categories
primary_categories = {
    # Equity
    "SEQ": {
        "SEQ_LC": "Large Cap",
        "SEQ_LMC": "Large & Mid Cap",
        "SEQ_FC": "Flexi Cap",
        "SEQ_MLC": "Multi Cap",
        "SEQ_MC": "Mid Cap",
        "SEQ_SC": "Small Cap",
        "SEQ_VAL": "Value",
        "SEQ_ELSS": "ELSS",
        "SEQ_CONT": "Contra",
        "SEQ_DIVY": "Dividend Yield",
        "SEQ_FOC": "Focused",
        "SEQ_SCTH": "Sectoral / Thematic",
    },
    # Solution Oriented
    "SSO": {
        "SSO_CHILD": "Children's",
        "SSO_RETR": "Retirement",
    },
    # Other
    "SOTH": {
        "SOTH_IXETF": "Index Funds/ ETFs",
        "SOTH_FOFS": "FoFs (Overseas/Domestic)",
    },
    # Debt
    "SDT": {
        "SDT_LND": "Long Duration",
        "SDT_MLD": "Medium to Long Duration",
        "SDT_MD": "Medium Duration",
        "SDT_SD": "Short Duration",
        "SDT_LWD": "Low Duration",
        "SDT_USD": "Ultra Short Duration",
        "SDT_LIQ": "Liquid",
        "SDT_MM": "Money Market",
        "SDT_OVNT": "Overnight",
        "SDT_DB": "Dynamic Bond",
        "SDT_CB": "Corporate Bond",
        "SDT_CR": "Credit Risk",
        "SDT_BPSU": "Banking and PSU",
        "SDT_FL": "Floater",
        "SDT_FMP": "FMP",
        "SDT_GL": "Gilt",
        "SDT_GL10CD": "Gilt with 10 year constant duration",
    },
    # Hybrid
    "SHY": {
        "SHY_AH": "Aggressive Hybrid",
        "SHY_BH": "Balanced Hybrid",
        "SHY_CH": "Conservative Hybrid",
        "SHY_EQS": "Equity Savings",
        "SHY_AR": "Arbitrage",
        "SHY_MAA": "Multi Asset Allocation",
        "SHY_DAABA": "Dynamic Asset Allocation or Balanced Advantage",
    },
}

# Define the columns for the scheme data
scheme_data = [
    [
        "Scheme Name",
        "Scheme Code",
        "NAV Date",
        "AMC",
        "Benchmark",
        "Plan",
        "Primery Category",
        "Category",
        "Theme/Sector",
        "Risk",
        "AUM",
        "Expense Ratio",
        "Rating",
        "Min SIP",
        "Min Investment One time",
        "Exit Load",
        "Benchmark Risk",
        "Return 3 months",
        "Return 6 months",
        "Return 1 year",
        "Return 1 year Benchmark",
        "Return 3 years",
        "Return 3 year Benchmark",
        "Return 5 years",
        "Return 5 year Benchmark",
        "Return 10 years",
        "Return 10 year Benchmark",
        "Return Since Inception",
        "Return Since Inception Benchmark",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Alpha",
        "Beta",
        "Standard Deviation",
    ],
]

# mapping of scheme columns to the ones in csv file for direct schemes
column_mapping_direct = {
    "Scheme Name": "Scheme Name",
    "Scheme Code": None,
    "NAV Date": None,
    "AMC": None,
    "Benchmark": "Benchmark",
    "Plan": None,
    "Primery Category": None,
    "Category": None,
    "Theme/Sector": None,
    "Risk": "Riskometer Scheme",
    "Benchmark Risk": "Riskometer Benchmark",
    "AUM": "Daily AUM (Cr.)",
    "NAV": "NAV Direct",
    "Expense Ratio": None,
    "Rating": None,
    "Min SIP": None,
    "Min Investment One time": None,
    "Exit Load": None,
    "Return 3 months": None,
    "Return 6 months": None,
    "Return 1 year": "Return 1 Year (%) Direct",
    "Return 1 year Benchmark": "Return 1 Year (%) Benchmark",
    "Return 3 years": "Return 3 Year (%) Direct",
    "Return 3 year Benchmark": "Return 3 Year (%) Benchmark",
    "Return 5 years": "Return 5 Year (%) Direct",
    "Return 5 year Benchmark": "Return 5 Year (%) Benchmark",
    "Return 10 years": "Return 10 Year (%) Direct",
    "Return 10 year Benchmark": "Return 10 Year (%) Benchmark",
    "Return Since Launch": "Return Since Launch Direct",
    "Return Since Launch Benchmark": "Return Since Launch Benchmark",
    "Sharpe Ratio": None,
    "Sortino Ratio": None,
    "Alpha": None,
    "Beta": None,
    "Standard Deviation": None,
}

# mapping of scheme columns to the ones in csv file for regular schemes
column_mapping_regular = {
    "Scheme Name": "Scheme Name",
    "Scheme Code": None,
    "NAV Date": None,
    "AMC": None,
    "Benchmark": "Benchmark",
    "Plan": None,
    "Primery Category": None,
    "Category": None,
    "Theme/Sector": None,
    "Risk": "Riskometer Scheme",
    "Benchmark Risk": "Riskometer Benchmark",
    "AUM": "Daily AUM (Cr.)",
    "NAV": "NAV Regular",
    "Expense Ratio": None,
    "Rating": None,
    "Min SIP": None,
    "Min Investment One time": None,
    "Exit Load": None,
    "Return 3 months": None,
    "Return 6 months": None,
    "Return 1 year": "Return 1 Year (%) Regular",
    "Return 1 year Benchmark": "Return 1 Year (%) Benchmark",
    "Return 3 years": "Return 3 Year (%) Regular",
    "Return 3 year Benchmark": "Return 3 Year (%) Benchmark",
    "Return 5 years": "Return 5 Year (%) Regular",
    "Return 5 year Benchmark": "Return 5 Year (%) Benchmark",
    "Return 10 years": "Return 10 Year (%) Regular",
    "Return 10 year Benchmark": "Return 10 Year (%) Benchmark",
    "Return Since Launch": "Return Since Launch Regular",
    "Return Since Launch Benchmark": "Return Since Launch Benchmark",
    "Sharpe Ratio": None,
    "Sortino Ratio": None,
    "Alpha": None,
    "Beta": None,
    "Standard Deviation": None,
}


def get_last_weekday_date() -> str:
    """
    Date of the last weekday in the format "dd-MMM-YYYY".

    :return: The date of the last weekday.
    """
    today = datetime.now()
    if today.weekday() >= 5:  # 5 and 6 corresponds to Saturday and Sunday
        last_weekday_date = today - timedelta(days=today.weekday() - 4)
    else:  # If today is a weekday, get the previous day's date
        last_weekday_date = today - timedelta(days=1)
    return last_weekday_date.strftime("%d-%b-%Y")


def get_data_from_url(
    url: str,
    params: Dict[str, str],
    headers: Dict[str, str],
    max_retries: int,
    wait_time: int,
) -> Optional[bytes]:
    """
    Get data from the given URL.

    :param url: The URL to get data from.
    :param params: The parameters to send with the request.
    :param headers: The headers to send with the request.
    :param max_retries: The maximum number of retries.
    :param wait_time: The wait time in seconds.
    :return: The content of the response if the request is successful, else None.
    """
    for retry_count in range(max_retries):
        try:
            response = httpx.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as error:
            logging.exception(f"An HTTP error occurred. Error: {error}")
            if retry_count < max_retries - 1:  # no need to wait after the last attempt
                time.sleep(wait_time)
        except Exception as error:
            logging.exception(f"An error occurred. Error: {error}")
            if retry_count < max_retries - 1:  # no need to wait after the last attempt
                time.sleep(wait_time)
    return None


def write_to_temp_file(content: bytes, suffix: str) -> str:
    """
    Write content to a temporary file.

    :param content: The content to write to the file.
    :param suffix: The suffix of the temporary file.

    :return: The name of the temporary file.
    """
    file_name = ""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        file_name = temp_file.name
        temp_file.write(content)
        temp_file.flush()
        os.fsync(temp_file.fileno())
    return file_name


def write_xls_sheet_to_csv(
    sheet: xlrd.sheet.Sheet,
    file_name: str,
    skip_row: int,
) -> None:
    """
    This function writes the xls sheet to a CSV file.

    :param sheet: The sheet to write to the CSV file.
    :param file_name: The name of the CSV file.
    :param skip_row: The number of rows to skip.
    """
    with open(file_name, "w", newline="") as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        for rownum in range(skip_row, sheet.nrows):
            wr.writerow(sheet.row_values(rownum))


def write_list_to_scheme_data(file_name: str) -> None:
    """
    This function writes scheme_data to a CSV file.

    :param file_name: The name of the CSV file.
    """
    with open(file_name, "w", newline="") as file:
        writer = csv.writer(file)
        for row in scheme_data:
            writer.writerow(row)


def read_from_excel(file_name: str) -> xlrd.sheet.Sheet:
    """
    This function reads an Excel file and returns the first sheet.

    :param file_name: The name of the Excel file.
    :return: The first sheet of the Excel file.
    """
    workbook = xlrd.open_workbook(file_name, ignore_workbook_corruption=True)
    return workbook.sheet_by_index(0)


def read_from_csv(file_name: str) -> List[Dict[str, str]]:
    """
    This function reads a CSV file and returns a list of dictionaries.

    :param file_name: The name of the CSV file.

    :return: A list of dictionaries.
    """
    with open(file_name, "r") as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=",")
        return list(csv_reader)


def fill_default_scheme_data(  # noqa: WPS211, DAR101, WPS213
    primary_category: str,
    category: str,
    nav_date: str,
    amc: str,
    scheme_data_column: str,
    scheme_data_row_direct: List[Any],
    scheme_data_row_regular: List[Any],
) -> Tuple[List[Any], List[Any]]:
    """
    This function fills the default scheme data.

    :param primary_category: The primary category of the scheme.
    :param category: The category of the scheme.
    :param nav_date: The NAV date of the scheme.
    :param amc: The AMC of the scheme.
    :param scheme_data_column: The column of the scheme data.
    :param scheme_data_row_direct: The row of the direct scheme data.
    :param scheme_data_row_regular: The row of the regular scheme data.

    :return: The updated rows of the direct and regular scheme data.
    """
    if scheme_data_column == "NAV Date":
        scheme_data_row_direct.append(nav_date)
        scheme_data_row_regular.append(nav_date)
    if scheme_data_column == "Primery Category":
        scheme_data_row_direct.append(primary_category)
        scheme_data_row_regular.append(primary_category)
    if scheme_data_column == "Category":
        scheme_data_row_direct.append(category)
        scheme_data_row_regular.append(category)
    if scheme_data_column == "Plan":
        scheme_data_row_direct.append("Direct")
        scheme_data_row_regular.append("Regular")
    if scheme_data_column == "AMC":
        scheme_data_row_direct.append(amc)
        scheme_data_row_regular.append(amc)
    return scheme_data_row_direct, scheme_data_row_regular


def fill_scheme_data(  # noqa: WPS210
    data: List[Dict[str, Any]],
    primary_category: str,
    category: str,
    nav_date: str,
    amc: str,
) -> None:
    """
    This function fills the scheme data.

    :param data: The data to fill the scheme data with.
    :param primary_category: The primary category of the scheme.
    :param category: The category of the scheme.
    :param nav_date: The NAV date of the scheme.
    :param amc: The AMC of the scheme.
    """
    for row in data:
        scheme_data_row_direct: List[Any] = []
        scheme_data_row_regular: List[Any] = []
        for scheme_data_column in scheme_data[0]:
            if scheme_data_column in {
                "NAV Date",
                "Primery Category",
                "Category",
                "Plan",
                "AMC",
            }:
                (
                    scheme_data_row_direct,
                    scheme_data_row_regular,
                ) = fill_default_scheme_data(
                    primary_category,
                    category,
                    nav_date,
                    amc,
                    scheme_data_column,
                    scheme_data_row_direct,
                    scheme_data_row_regular,
                )
                continue
            csv_column_direct = column_mapping_direct.get(scheme_data_column)
            csv_column_regular = column_mapping_regular.get(scheme_data_column)
            if csv_column_direct is not None:
                scheme_data_row_direct.append(row[csv_column_direct])
            else:
                scheme_data_row_direct.append(None)

            if csv_column_regular is not None:
                scheme_data_row_regular.append(row[csv_column_regular])
            else:
                scheme_data_row_regular.append(None)
        scheme_data.append(scheme_data_row_direct)
        scheme_data.append(scheme_data_row_regular)


def main() -> None:  # noqa: WPS210, WPS213
    """Main."""
    base_url = "https://www.valueresearchonline.com/downloads/amfi-performance-xls/"
    nav_date = get_last_weekday_date()
    amc = "ALL"
    max_retries = 3  # maximum number of retries
    wait_time = 2  # wait time in seconds
    end_type = "1"  # Open Ended
    headers = {
        "Referer": "https://www.valueresearchonline.com/amfi/fund-performance",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    for primary_category, categories in primary_categories.items():
        for category, _ in categories.items():
            params = {
                "source_url": f"/amfi/fund-performance-data/?end-type={end_type}"
                f"&primary-category={primary_category}&category={category}"
                f"&amc={amc}&nav-date={nav_date}",
            }

            try:
                content = get_data_from_url(
                    base_url,
                    params,
                    headers,
                    max_retries,
                    wait_time,
                )
                if content is None:
                    logging.info(
                        f"No content for primary_category: {primary_category} and "
                        f"category: {category} and date: {nav_date} and amc: {amc}",
                    )
                    continue

                temp_xlsx_file_name = write_to_temp_file(content, ".xlsx")
                sheet = read_from_excel(temp_xlsx_file_name)

                temp_csv_file_name = temp_xlsx_file_name.replace(".xlsx", ".csv")
                # skip first 5 rows as they are not needed
                write_xls_sheet_to_csv(sheet, temp_csv_file_name, 5)

                data = read_from_csv(temp_csv_file_name)
                fill_scheme_data(data, primary_category, category, nav_date, amc)

                os.remove(temp_xlsx_file_name)
                os.remove(temp_csv_file_name)
            except httpx.HTTPStatusError as error:
                logging.exception(
                    f"An HTTP error occurred for primary_category: {primary_category} "
                    f"and category: {category} and date: {nav_date} and amc: {amc}. "
                    f"Error: {error}",
                )
            except Exception as error:
                logging.exception(
                    f"An error occurred for primary_category: {primary_category} and "
                    f"category: {category} and date: {nav_date} and amc: {amc}. "
                    f"Error: {error}",
                )

    scheme_data_file = f"scheme_data_{nav_date}.csv"
    write_list_to_scheme_data(scheme_data_file)


if __name__ == "__main__":
    main()
