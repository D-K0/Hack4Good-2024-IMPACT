"""
get a list of all the months in the data range including the missing months
"""

from datetime import datetime
import pandas as pd

def find_matching_id(data, date):
    """find an index of a month

    Args:
        data (dataframe): data that is being croped
        date (String): date the is being looked up

    Returns:
        int: index of the month that is being looked up
    """
    try:
        matching_index = data.index[data['year_month'] == date][0]
        return matching_index
    except IndexError:
        return -1

def remover_early_months(data, min_date): # min_date = '2016-03'
    """cut out dates before the max month of interest

    Args:
        data (dataframe): data of an admin
        min_date (String): min date in the range

    Returns:
        dataframe: data without the too early months
    """
    min_month_id = find_matching_id(data, min_date)
    cut_data = data.copy()[min_month_id:].reset_index(drop=True)
    return cut_data

def remover_late_months(data, max_date):
    """cut out dates beyond the max month of interest

    Args:
        data (dataframe): data of an admin
        max_date (String): max date in the range

    Returns:
        dataframe: data without the too late months
    """
    max_month_id = find_matching_id(data, max_date)
    cut_data = data.copy()[:max_month_id+1].reset_index(drop=True)
    return cut_data

def find_missing_months(start, end):
    """determine a full list of months

    Args:
        start (String): earlier month
        end (String): latest month

    Returns:
        list of string: list of all the motnhs
    """
    # Generate a list of full date range (no missing months)
    start_date = pd.to_datetime(start, format='%Y-%m') # The earliest date
    end_date = pd.to_datetime(end, format='%Y-%m')  # The latest date
    # Generate all months in the range
    full_date_range = pd.date_range(start=start_date, \
                                    end=end_date, freq='MS').strftime('%Y-%m').tolist()
    return full_date_range

def get_full_dates_list(data_partial, min_date = None, max_date=None):
    """get a list of all the months in the data range including the missing months
    Args:
        data_partial (dataframe): data that is being inspected
        min_date (string, optional): minimum month of the data range. Defaults to None.
        max_date (striing, optional): max month of th data, excluding fututre months. 
                                        Defaults to None.
    """
    def get_datetime(date):
        return datetime.strptime(date, '%Y-%m')

    data = data_partial.copy()

    if min_date is None:
        min_date = data['year_month'].iloc[0]
    if max_date is None:
        max_date = data['year_month'].iloc[-1]

    earliest_data = data['year_month'].iloc[0]
    latest_data = data['year_month'].iloc[-1]

    if get_datetime(latest_data) > get_datetime(max_date):
        data = remover_late_months(data, max_date=max_date)
        latest_data = max_date

    if get_datetime(earliest_data) < get_datetime(min_date):
        data = remover_early_months(data, min_date=min_date)
    earliest_data = min_date

    months_lst = sorted(find_missing_months(earliest_data, latest_data))

    return months_lst, data
