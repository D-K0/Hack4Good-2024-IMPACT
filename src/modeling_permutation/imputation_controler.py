"""
    controler of imputation stage
"""
import logging

from preprocessing.data_loading import data_loading

from modeling_permutation.admin1_dataset_creater import create_admin1_dataset
from modeling_permutation.admin_2_3_dataset_creater import create_admin_2_3_dataset
# from modeling_permutation.prim_imputations import basic_impute_data
from calculate_meb import mult_admin_meb

from modeling_permutation.global_regression import perform_global_regression_imputation
from modeling_permutation.local_regression import perform_local_regression_imputation

from set_up.constants import PRODUCTS_LABELS, ADMIN_LOCATIONS
from set_up.addresses_constants import ADRS_IMPUTED

log = logging.getLogger(__name__)  # Logger for this module

def create_admin0_dataset(data):
    """imputed admin level 0 data

    Args:
        data (dataframe): admin 0 level data

    Returns:
        dataframe: imputed admin level 0
    """
    # imputed_data = basic_impute_data(data)
    #perform a local regression followed by a global regression for data imputation
    admin_0_df = data.copy()
    for product in PRODUCTS_LABELS:
        single_price_df = admin_0_df[product]
        single_price_df = single_price_df.reset_index().drop(columns = ["index"])
        perform_local_regression_imputation(single_price_df)
        perform_global_regression_imputation(single_price_df, dim = 3)
        admin_0_df[product] = single_price_df
    return admin_0_df

def perm_admin(admin_label, raw_admin, preprocessed_df = None, higher_admin_final_dataset=None):
    """permute a given admin level

    Args:
        admin_label (String): admin level in question
        raw_admin (dataframe): raw data of an admin
        preprocessed_df (dataframe, optional): preprocessed data. Defaults to None.
        higher_admin_final_dataset (dataframe, optional): imputed data of the previous level. 
                                                            Defaults to None.
    Returns:
        dataframe: imputed data of a given data level
    """
    if admin_label == 'admin0_label' or admin_label is None:
        log.info("Start Imputation for the averaged data")
        return create_admin0_dataset(raw_admin[admin_label])
    elif admin_label == 'admin1_label':
        log.info("Start Imputation for admin1_label data (may take more than 20 min)")
        # this method may take around 20 minutes to run
        return create_admin1_dataset(raw_admin[admin_label], admin_label)
    elif admin_label in ('admin2_label', 'admin3_label'):
        log.info("Start Imputation for admin2 or admin3 data")
        return create_admin_2_3_dataset(raw_admin[admin_label], admin_label, \
                                        higher_admin_final_dataset, preprocessed_df)
    print("error")
    return None

def imput_controler(preprocessed_df, raw_admin):
    """impute data at diffrent admin level 

    Args:
        preprocessed_df (dataframe): preprocessed raw data
        raw_admin (dictionary of dataframes): raw data seperated by admins

    Returns:
        dictionary of dataframes: imputed data
        dictionary of dataframes: imputed data with meb
    """
    data_wihtout_meb = {}
    imputed_data = {}

    if "admin0_label" in ADMIN_LOCATIONS:
        log.info("perform admin 0 imputation")
        data_wihtout_meb["admin0_label"] = perm_admin("admin0_label", raw_admin)

    if "admin1_label" in ADMIN_LOCATIONS:
        log.info("perform admin 1 imputation")
        data_wihtout_meb["admin1_label"] = perm_admin("admin1_label", raw_admin)
    elif "admin2_label" in ADMIN_LOCATIONS or "admin3_label" in ADMIN_LOCATIONS:
        log.info("load admin 1 imputation")
        data_wihtout_meb["admin1_label"] = data_loading(ADRS_IMPUTED['admin1_label'])

    if "admin2_label" in ADMIN_LOCATIONS:
        log.info("perform admin 2 imputation")
        data_wihtout_meb["admin2_label"] = perm_admin("admin2_label", raw_admin, preprocessed_df, \
                                                      higher_admin_final_dataset=\
                                                        data_wihtout_meb["admin1_label"])
    elif "admin3_label" in ADMIN_LOCATIONS:
        log.info("load admin 2 imputation")
        data_wihtout_meb["admin2_label"] = data_loading(ADRS_IMPUTED['admin2_label'])

    if "admin3_label" in ADMIN_LOCATIONS:
        log.info("perform admin 3 imputation")
        data_wihtout_meb["admin3_label"] = perm_admin("admin3_label", raw_admin, preprocessed_df, \
                                                      higher_admin_final_dataset=\
                                                        data_wihtout_meb["admin2_label"])

    log.info("perform MEB calculation")
    imputed_data = mult_admin_meb(data_wihtout_meb.copy())
    return data_wihtout_meb, imputed_data
