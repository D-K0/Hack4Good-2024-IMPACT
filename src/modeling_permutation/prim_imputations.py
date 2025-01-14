"""
primitive data imputation to fill in empty data rows using closes existing values
"""
import logging

import numpy as np

log = logging.getLogger(__name__)  # Logger for this module

def look_for_neighbour_value(data_col, id_value, cursor_shift, direction):
    """search for the closest non empty values

    Args:
        data_col (dataframe's column): column of product prices
        id_value (int): index value of the inspected missing cell
        cursor_shift (int): index of the location that is being checked for values
        direction (int): direction of the search

    Returns:
        int: one of the closest neighbouring values
        int: newst position of the look up cursor

    """
    if cursor_shift == np.inf or cursor_shift == -np.inf:
        return None, np.inf
    cursor = id_value + cursor_shift*direction
    if cursor <= 0 or cursor >= len(data_col):
        return None, np.inf
    if not np.isnan(data_col[cursor]):
        return data_col[cursor], cursor_shift
    return look_for_neighbour_value(data_col, id_value, cursor_shift+1, direction)

def get_neighbours_values(column, index):
    """find the closes 4 values of a specific empty cell

    Args:
        column: product column in the dataset
        index (int): the index of the assessed missing data point

    Returns:
        list: the 4 closest values of the observed data cell
    """
    neighbours_values_list = []
    e1, cursor_shift = look_for_neighbour_value(column, index, 1, -1)
    e2, cursor_shift = look_for_neighbour_value(column, index, cursor_shift+1, -1)
    e3, cursor_shift = look_for_neighbour_value(column, index, 1, 1)
    e4, cursor_shift = look_for_neighbour_value(column, index, cursor_shift+1, 1)
    if e1 is not None:
        neighbours_values_list.append(e1)
    if e2 is not None:
        neighbours_values_list.append(e2)
    if e3 is not None:
        neighbours_values_list.append(e3)
    if e4 is not None:
        neighbours_values_list.append(e4)
    return neighbours_values_list

def neighbour_imputation(data):
    """calculation of the 4 closest average values.

    Args:
        data (pandas dataframe): admin 0 data frame

    Returns:
        dataframe:  imputed admin 0 data
    """
    data_imputed = data.copy()

    for column_name in data_imputed.columns:
        if column_name != 'year_month':
            column = data_imputed[column_name]
            missing_data_id = column[column.isna()].index
            for index in missing_data_id:
                neighbours_values_list = get_neighbours_values(column, index)
                mean_value = sum(neighbours_values_list) / len(neighbours_values_list)
                data_imputed.loc[index, column_name] = mean_value

    return data_imputed

def basic_impute_data(data):
    """Imputation of adminless data, using the average 4 closest values

    Args:
        data (pandas dataframe): admin 0 data frame

    Returns:
        dataframe: imputed admin 0 data
    """
    data_imputed = neighbour_imputation(data)
    return data_imputed
