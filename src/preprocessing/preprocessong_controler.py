'''
    prepare data to be processed by the statistical models
'''
import logging

from preprocessing.remove_outliers import generate_outlierless_data
from preprocessing.data_cleaning import (isolate_relevant_goods_columns,
                                                replace_blank_with_nan,
                                                convert_months_to_num, concat_mont_year)
from preprocessing.gen_raw_admins import generate_raw_admins

log = logging.getLogger(__name__)  # Logger for this module

def preprocessong_controler(data, perform_outlier=True, min_date=None, max_date=None):
    """prepare data to be processed by the statistical models

    Args:
        data (_type_): _description_
        perform_outlier (bool, optional): _description_. Defaults to True.
        min_date (_type_, optional): _description_. Defaults to None.
        max_date (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    log.info("Started preprocessing controler")
    frame_data = data.copy()

    log.info("Starting filtering")
    clean_data = isolate_relevant_goods_columns(frame_data)

    log.info("Starting to correct empty cells for NAN.")
    nan_data = replace_blank_with_nan(clean_data)

    log.info("Starting to remove empty rows")
    short_data = nan_data #remove_empty_rows(nan_data) #######gabriel 23.11

    if 'month' in short_data.columns:
        log.info("Starting to convert months from words to int.")
        numbered_data=convert_months_to_num(short_data)
        log.info("start concatonating year_month columns")
        adjusted_data=concat_mont_year(numbered_data)
    else:
        adjusted_data = short_data
        perform_outlier = False

    log.info("removing outliers")
    if perform_outlier:
        outlierless_data = generate_outlierless_data(adjusted_data)
    else:   outlierless_data = adjusted_data

    raw_admins = generate_raw_admins(outlierless_data, min_date, max_date)

    return outlierless_data, raw_admins
