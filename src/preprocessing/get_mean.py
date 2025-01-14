"""
generate the monthly average of data
"""
from set_up.constants import PRODUCTS_LABELS

def get_mean(data_raw, admin_level=None):
    """generate the monthly mean of the data.

    Args:
        data_raw (dataframe): raw data
        admin_level (String, optional): admin level. Defaults to None.

    Returns:
        dataframe: averaged data
    """
    data = data_raw.copy()
    # Define the list of price columns
    price_columns = PRODUCTS_LABELS

    # Choose the groupby columns based on admin_level
    if admin_level == 'admin0_label' or admin_level is None:
        groupby_columns = ['year_month']
    else:
        groupby_columns = ['year_month', admin_level]

    # Perform the groupby operation and calculate the mean for the price columns
    mean_data = data.groupby(groupby_columns)\
        .agg({col: 'mean' for col in price_columns}).reset_index()

    return mean_data
