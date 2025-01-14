"""
clean data as part of the preprocessing stage
"""

import numpy as np

from set_up.constants import PRODUCTS_LABELS

def isolate_relevant_goods_columns(data):
    """filter the data to have only the relevant columns

    Args:
        data (dataframe): raw data

    Returns:
        dataframe: filtered data
    """
    all_relelvant_labels = ['uuid', 'year_month', 'date', 'year', 'month', 'admin1_code',
                            'admin1_label', 'admin2_code', 'admin2_label', 'admin3_code',  
                            'admin3_label', 'admin4_code', 'admin4_label', 'urban_rural',
                            'meb', 'bulgur_price','rice_price', 'bread_price', 
                            'lentil_price', 'vegetable_oil_price','sugar_price', 'salt_price', 
                            'tomato_price', 'potato_price', 'onion_price', 'cucumber_price', 
                            'chicken_meat_price', 'egg_price', 'tomato_paste_price',
                            'soap_price','laundry_soap_bar_price', 'toothpaste_price', 
                            'sanitary_pad_price', 'kerosene_manually_refined_price']
    present_labels = [label for label in all_relelvant_labels if label in data.columns]
    relevant_goods_data = data[present_labels]
    return relevant_goods_data

def replace_blank_with_nan(data):
    """replace any blank or None cells with NAN

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    data_w_nan = data.copy()
    data_w_nan = data_w_nan.replace('', np.nan, inplace=True)
    if data_w_nan is None:
        return data
    return data_w_nan # if no nan to remove

def remove_empty_rows(data):
    """remove any empty rows

    Args:
        data (dataframe): raw data

    Returns:
        dataframe: shorter data
    """
    shorter_data = data.dropna(subset=PRODUCTS_LABELS, how = 'all').reset_index(drop=True)
    return shorter_data

def convert_months_to_num(data):
    """ conver the months from word to number format

    Args:
        data (dataframe): data with word months

    Returns:
        dataframe: data with number months
    """
    month_to_number = {
        'January': '1', 'February': '2', 'March': '3', 'April': '4',
        'May': '5', 'June': '6', 'July': '7', 'August': '8',
        'September': '9', 'October': '10', 'November': '11', 'December': '12',
        1 : '1' , 2 : '2',  3 :  '3',  4 :  '4' ,  5 :  '5' , 6 : '6', 7 : '7',
        8 : '8' , 9 : '9', 10 : '10', 11 : '11' , 12 : '12'
    }
    relevant_goods_data = data.copy()
    # Replace the month names with corresponding numbers
    relevant_goods_data['month'] = relevant_goods_data['month'].map(month_to_number)
    return relevant_goods_data

def concat_mont_year(data):
    """convert the 'date' column of format yyyy-mm-dd to 'year_month' of the format yyyy-mm

    Args:
        data (dataframe): data with date column

    Returns:
        dataframe: data with year-month column
    """
    adjusted_data = data.copy()
    adjusted_data['year_month'] = data['year'].astype(str) + '-' \
        + data['month'].astype(str).str.zfill(2)
    adjusted_data.drop(columns=['year', 'month'], inplace=True)
    cols = adjusted_data.columns.tolist()  # Get a list of all columns
    cols.insert(1, cols.pop(cols.index('year_month')))
    adjusted_data = adjusted_data[cols]
    return adjusted_data
