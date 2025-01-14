"""
    load data
"""

import logging

import pandas as pd
from python_calamine import CalamineWorkbook
import pyarrow
from pyarrow import csv

log = logging.getLogger(__name__)  # Logger for this module

# Load file in diffrent formats
def load_xlsx_file(adrs):
    """load data from xlsx

    Args:
        adrs (String): data address

    Returns:
        TBD: loaded data (data needs to be checked)
    """
    return CalamineWorkbook.from_path(adrs).get_sheet_by_index(0).to_python(skip_empty_area=False)

def load_csv_file(adrs):
    """load data from csv

    Args:
        adrs (String): data address

    Returns:
        TBD: loaded data (data needs to be checked)
    """
    return csv.read_csv(adrs)

def load_parquet_file(adrs):
    """load data from parquet

    Args:
        adrs (String): data address

    Returns:
        TBD: loaded data (data needs to be checked)
    """
    return pd.read_parquet(adrs)

def check_csv_extension(adrs):
    """check extention type is csv

    Args:
        adrs (String): data loading address

    Returns:
        bool: return if the type is expected
    """
    return adrs.lower().endswith('.csv')

def check_xlsx_extension(adrs):
    """check extention type is xlsx

    Args:
        adrs (String): data loading address

    Returns:
        bool: return if the type is expected
    """
    return adrs.lower().endswith('.xlsx')

def check_parquet_extension(adrs):
    """check extention type is parquet

    Args:
        adrs (String): data loading address

    Returns:
        bool: return if the type is expected
    """
    return adrs.lower().endswith('.parquet')

def load_raw_data_by_extention(adrs):
    """check extention type

    Args:
        adrs (String): data loading address

    Returns:
        dataframe: return loaded data; type depends on what extention was loaded
    """
    if check_csv_extension(adrs):
        return load_csv_file(adrs)
    if check_xlsx_extension(adrs):
        return load_xlsx_file(adrs)
    if check_parquet_extension(adrs):
        return load_parquet_file(adrs)
    return 'No valid file type detected.'

# create a data framework to work with
def convert_list_to_data_frame(workbook):
    """convert list data into dataframe

    Args:
        workbook (list): loaded data

    Returns:
        dataframe: converted data
    """
    raw_full_data = pd.DataFrame(workbook)
    return raw_full_data

def generate_headers(data):
    """add headers to the columns if they are not there

    Args:
        data (dataframe): data where the headers are inside the column

    Returns:
        dataframe: data with column headers
    """
    new_header = data.iloc[0]
    data = data.iloc[1:]
    data.columns = new_header
    data.reset_index(drop=True, inplace = True)
    return data

def convert_table_to_data_frame(table):
    """convert table to pandas dataframe

    Args:
        table (pyarrow.lib.Table): table data

    Returns:
        dataframe: converted data
    """
    data_frame = table.to_pandas()
    return data_frame

def convert_to_data_frame(raw_data):
    """convert raw data to dataframe

    Args:
        raw_data: loaded data

    Returns:
        fataframe: converted data
    """
    if isinstance(raw_data, list):
        data = convert_list_to_data_frame(raw_data)
        data = generate_headers(data)
        return data
    elif isinstance(raw_data, pyarrow.lib.Table):  # pylint: disable=c-extension-no-member
        return convert_table_to_data_frame(raw_data)
    elif isinstance(raw_data, pd.core.frame.DataFrame):
        return raw_data
    else:
        print("ERROR!!!! invalid data type for conversion to data frame.")
        return 0

def convert_table_to_parquet(table, adrs):
    """export pyarrow.lib.Table as parquet

    Args:
        table (pyarrow.lib.Table):  loaded data
        adrs (String): export address

    Returns:
        bool: return 1 for succsseful action
    """
    adrs_out = './../../data/raw/' + adrs[adrs.rfind('\\')+1:adrs.rfind('.')] + '.parquet'
    pyarrow.parquet.write_table(table, adrs_out)
    return 1

# main controler function
def data_loading(adrs, convert2parquet = False):
    """load data from a csv/xlsx/parquest file.
    CSV FILE TYPE IS STRONGLY RECOMDED
    (to get a csv file from xlsx use excel app for fastes results)

    Args:
        adrs (string): the data adress
        convert2parquet (bool, optional): flag to convert data to parquet for 
                                            future use. Defaults to False.

    Returns:
        dataframe: loaded data as a dataframe
    """
    log.info("Started loading data from file")
    raw_data = load_raw_data_by_extention(adrs)
    log.info("data has been loaded")

    if convert2parquet:
        log.info("Started generating parquet file")
        convert_table_to_parquet(raw_data, adrs)
        adrs_out = './../../data/raw/' + adrs[adrs.rfind('\\')+1:adrs.rfind('.')] + '.parquet'
        log.info("parquest file has been generated at: %s.parquet", adrs_out)

    log.info("started converting raw data format to panda dataframe")
    frame_data = convert_to_data_frame(raw_data)

    return frame_data
