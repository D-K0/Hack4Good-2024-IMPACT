"""
    _summary_
"""
import logging

from set_up.constants import PRODUCTS_LABELS, PRODUCT_MEB_QUANTITIES

log = logging.getLogger(__name__)  # Logger for this module

def mult_admin_meb(og_data):
    """_summary_

    Args:
        og_data (dataframe): dictionary of admin dataframes

    Returns:
        dictionary: data of diffrent admins with meb calculated
    """
    data = og_data.copy()
    for admin_label in data.keys():
        data[admin_label] = generate_average_meb(data[admin_label], admin_label)
    return data

def generate_average_meb(data_input, admin_label):
    """
    Calculates the Minimum Expenditure Basket (MEB) for 
    selected products based on their quantities and prices.

    Parameters:
        data (DataFrame): The input data containing product prices.
        product_labels (list): List of product labels (subset of the product names in the data).

    Returns:
        DataFrame: Updated DataFrame with the MEB column calculated.
    """
    logging.info("Start MEB calculation.")

    data = data_input.copy()
    # Validate product labels
    if not set(PRODUCTS_LABELS).issubset(set(PRODUCT_MEB_QUANTITIES.keys())):
        missing_products = set(PRODUCTS_LABELS) - set(PRODUCT_MEB_QUANTITIES.keys())
        raise ValueError(f"Missing quantities for products: {missing_products}")

    # Filter the quantities dictionary to only include the selected product labels
    quantities = {product: PRODUCT_MEB_QUANTITIES[product] for product in PRODUCTS_LABELS}

    # Ensure all required columns exist in the DataFrame
    missing_columns = set(PRODUCTS_LABELS) - set(data.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in the DataFrame: {missing_columns}")

    # Remove the existing 'meb' column if it exists
    if 'meb' in data.columns:
        logging.warning("'meb' column already exists and will be deleted and re-calculated.")
        data.drop(columns=['meb'], inplace=True)

    # Ensure the columns are aligned with the order of product_labels in quantities
    aligned_prices = data.reindex(columns=PRODUCTS_LABELS)

    # Extract quantities corresponding to product_labels
    ordered_quantities = [quantities[label] for label in aligned_prices.columns]

    # Calculate the MEB
    data['meb'] = aligned_prices.multiply(ordered_quantities, axis=1).sum(axis=1, skipna=True)

    # Move MEB column to the second or thirds position
    cols = data.columns.tolist()
    if admin_label == 'admin0_label':
        cols.insert(1, cols.pop(cols.index('meb')))
    elif admin_label in ['admin1_label', 'admin2_label', 'admin3_label', 'admin4_label']:
        cols.insert(2, cols.pop(cols.index('meb')))
    else:
        raise ValueError("correct admin label not found")
    data = data[cols]

    return data
