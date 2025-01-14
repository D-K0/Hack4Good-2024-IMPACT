"""
    generate a dictionary of raw data frames by admin level
"""
import pandas as pd

from set_up.constants import ADMIN_LOCATIONS, MIN_DATE, MAX_DATE
from preprocessing.complete_months_list import get_full_dates_list
from preprocessing.get_mean import get_mean

def merge_missing_months_n_data(data, date_range, admin_level):
    """add missing months into the dataframe

    Args:
        data (dataframe): raw data of an admin
        date_range (list): list of months within the data range
        admin_level (String): in the name

    Returns:
        dataframe: raw data with the missing motnhs as nan
    """
    if admin_level == 'admin0_label' or admin_level is None:
        full_index = pd.MultiIndex.from_product([date_range], names=['year_month'])
    else:
        cities = ADMIN_LOCATIONS[admin_level]
        full_index = pd.MultiIndex.from_product([date_range, cities],
                                                names=['year_month', admin_level])

    full_df =  pd.DataFrame(index=full_index).reset_index()

    if admin_level == 'admin0_label' or admin_level is None:
        merged_data = pd.merge(full_df, data, on=['year_month'], how='left')
    else:
        merged_data = pd.merge(full_df, data, on=['year_month', admin_level], how='left')
        merged_data.reset_index()
    return merged_data

def get_single_admin(data, admin_level, min_date=MIN_DATE, max_date=MAX_DATE):
    """seperate the data of the specific admin

    Args:
        data (dataframe): preprocess data
        admin_level (String): admin level in question
        min_date (String, optional): minimum date. Defaults to MIN_DATE.
        max_date (String, optional): max date. Defaults to MAX_DATE.

    Returns:
        dataframe: data after being seperated and cut as needed
    """
    mean_data = get_mean(data, admin_level)
    date_range, cut_data = get_full_dates_list(mean_data, min_date, max_date)
    full_admin = merge_missing_months_n_data(cut_data, date_range, admin_level)
    return full_admin

def generate_raw_admins(raw_data, min_date=MIN_DATE, max_date=MAX_DATE):
    """generate a dictionary of raw data frames by admin level

    Args:
        raw_data (dataframe): preprocessed data
        min_date (string, optional): min date of the data. Defaults to MIN_DATE.
        max_date (string, optional):  max date of the data. Defaults to MAX_DATE.

    Returns:
        dictionary of dataframe: data devided by admin level
    """
    raw_admin_data = {}
    for admin in ADMIN_LOCATIONS:
        raw_admin_data[admin] = get_single_admin(raw_data, admin, min_date, max_date)
    return raw_admin_data
