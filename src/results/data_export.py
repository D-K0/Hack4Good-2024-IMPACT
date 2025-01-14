"""
    export data
"""
import logging

from time import time
from pathlib import Path
from collections import defaultdict

import pandas as pd

from set_up.addresses_constants import ADRS_EXPORT_DIR
# needed for assigning values to TIME_FOLDER. it gets wonky otherwise
import set_up.addresses_constants as ac


log = logging.getLogger(__name__)  # Logger for this module

def export_csv(data_frame, adrs):
    """export data

    Args:
        data_frame (dataframe): data that is to be exported
        adrs (String): location to export

    Returns:
        bool: ` for success`
    """
    log.info("Started data export to csv file")
    data_frame.to_csv(adrs, sep=',', index=False, encoding='utf-8')
    log.info("exported data to %s", adrs)
    return 1

def export_df_n_dict(data, adress):
    """export dictionary of dataframes
    Args:
        data: <-
        adress (String): export address data
    """
    if isinstance(data, pd.DataFrame):
        export_csv(data, adress)
        print(adress)
    elif isinstance(data, (dict, defaultdict)):
        for admin_labels in data.keys():
            adress_admins = adress.replace('.csv', f'_{admin_labels}.csv')
            print(adress_admins)
            export_csv(data[admin_labels], adress_admins)
    elif len(data.keys()) == 0:
        print("data is empty !!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        raise TypeError(f"data cannot be exported. Provided data is type {type(data)}")

def define_dir():
    """create a directory for export if it doesnt exists yet
    the new directory depends on unix time as part of the path name

    Returns:
        String: name of the newly created directory
    """
    ac.TIME_FOLDER = str(int(time()))
    directory = ADRS_EXPORT_DIR + ac.TIME_FOLDER + '/'
    Path(directory).mkdir(parents=True, exist_ok=True)
    return directory

def imp_pred_dir(choice, adrs_imp=None, adrs_pred=None):
    """address to store imputed an dpredicted data

    Args:
        choice (int): task choice
        adrs_imp (String, optional): imputed data storage address; 
                                        if it already decided. Defaults to None.
        adrs_pred (String, optional): predicted data storage address; 
                                        if it already decided. Defaults to None.

    Returns:
        String: imputed data storage address
        String: predicted data storage address
    """
    current_dir = define_dir()
    if choice in [1, 2]:
        if adrs_imp is None:
            adrs_imp = current_dir + "imputed.csv"
    if choice in [2, 3]:
        if adrs_pred is None:
            adrs_pred = current_dir + "predicted.csv"
    return adrs_imp, adrs_pred

def export_controler(choice, imputed_data, predicted_data, adrs_imp=None, adrs_pred=None):
    """export data

    Args:
        choice (int): task choice
        imputed_data (dictionary of dataframe): <-
        predicted_data (dictionary of dataframe): <-
        adrs_imp (String, optional): address to store imputed data. Defaults to None.
        adrs_pred (String, optional): address to store predicted. Defaults to None.

    Returns:
        bool: return 1 if succful completion
    """
    adrs_imp, adrs_pred = imp_pred_dir(choice, adrs_imp, adrs_pred)
    if choice in {1, 2}:
        log.info("start exporting imputed data.")
        export_df_n_dict(imputed_data, adrs_imp)
    if choice in {2, 3}:
        log.info("start exporting predicted data.")
        export_df_n_dict(predicted_data, adrs_pred)
    return 1
