"""
visualize the data that has been process in a form of plot
and store in data/plot folder
"""
import logging

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from set_up.constants import (PRODUCTS_LABELS, PREDICT_PRODUCTS,
                              ADMIN_LOCATIONS, PREDICT_CITIES)
from set_up.addresses_constants import ADRS_DIR_PLOT, TIME_FOLDER

log = logging.getLogger(__name__)  # Logger for this module

def save_fig_loc(plt, admin_level, subject): # pylint: disable=redefined-outer-name
    """save the plot in the plotting file
    Args:
        plt: <-
        admin_level (String): <-
        subject (String): the subject that is being plotted (a region or a product)

    Returns:
        String: address where the plot was exported to 
    """
    directory = ADRS_DIR_PLOT + TIME_FOLDER + '/'
    Path(directory).mkdir(parents=True, exist_ok=True)
    plot_loc = directory + admin_level + '_' + subject + '.png'
    plt.savefig(plot_loc, format="png")
    log.info("eplot was saved to %s", plot_loc)
    return plot_loc

def plot_data(raw_data, imputed_data, subject, varity_label, # pylint: disable=too-many-arguments, too-many-branches
              admin_level , predicted_data = None):

    """plot data
    admin_level param is for saving the plot ONLY

    Args:
        raw_data (dataframe): raw data of an admin
        imputed_data (dataframe): imputed data of an admin
        subject (String): the subject whose data is being plotted
        varity_label (String): the column name of what is being varied
        admin_level (String): <-
        predicted_data (dataframe, optional): predicted data of an admin. Defaults to None.
    """
    list_of_months = imputed_data['year_month'].tolist()
    if varity_label == 'admin0_label':
        variation, varity_label = None, 'Syria'
    else:
        variation = varity_label
    # Plot for price over time
    plt.figure(figsize=(10, 6))

    if varity_label in ('admin0_label', 'Syria'):#
        if subject != 'meb':
            sns.scatterplot(data=raw_data, x='year_month', y=subject,
                            s=20)
        sns.lineplot(data=imputed_data, x='year_month', y=subject,
                    linewidth=1)

        try:
            sns.lineplot(data=predicted_data, x='year_month', y=subject,
                        marker='*', linewidth=2)
            list_of_months += predicted_data['year_month'].tolist()
        except Exception: # pylint: disable=broad-exception-caught
            log.info("An error occurred. Skipping plotting prediciton.")
    else:
        if subject != 'meb':
            sns.scatterplot(data=raw_data, x='year_month', y=subject,
                            hue=variation, palette='Set2', s=20)
        sns.lineplot(data=imputed_data, x='year_month', y=subject,
                    hue=variation, palette='Set1', linewidth=1)

        try:
            sns.lineplot(data=predicted_data, x='year_month', y=subject,
                        hue=variation, palette='Set1', marker='*', linewidth=2)
            list_of_months += predicted_data['year_month'].tolist()
        except Exception: # pylint: disable=broad-exception-caught
            log.info("An error occurred. Skipping plotting prediciton.")

    if varity_label == 'products':
        plt.title(subject + ' in ' + admin_level + ' price Over time for ' + varity_label)
    else:
        plt.title(subject + ' price Over time for ' + varity_label)
    list_months = list(set(list_of_months))
    list_months.sort()
    plt.xticks(np.arange(0, len(list_months), 6), labels=list_months[::6])  # Use every 6th label

    plt.xticks(rotation=45)
    plt.xlabel('Year-Month')
    plt.ylabel('Price')

    if varity_label not in ('admin0_label', 'Syria'):
        plt.legend(title=varity_label, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.grid()

    # plt.show()
    save_fig_loc(plt, admin_level, subject)
    plt.show()

def plot_product_prices_in_city(raw_data, imputed_data, admin_label, region, # pylint: disable=too-many-arguments, too-many-branches
                                product_list, predicted_data = None):
    """ plot diffrent products for a region 

    Args:
        raw_data (dataframe): raw data
        imputed_data (dataframe): imputed data
        admin_label (String): <-
        region (String): region which is being plotted
        product_list (List): list of proccessed products
        predicted_data (dataframe, optional): predicted data. Defaults to None.

    Returns:
        dataframe: raw data that is being plotted
        dataframe: imputed data that is being plotted
        dataframe: predictd data that is being plotted
    """
    raw_data = raw_data.copy()
    imputed_data = imputed_data.copy()
    if predicted_data is not None:
        predicted_data = predicted_data.copy()
    else:
        predicted_data = None

    # Filter the data for the specific city
    if admin_label != 'admin0_label':
        raw_city_data = raw_data[raw_data[admin_label] == region]
        imputed_city_data = imputed_data[imputed_data[admin_label] == region]
        if predicted_data is not None:
            if predicted_data is not None:
                pred_t = predicted_data[predicted_data[admin_label] == region]
        else:
            pred_t = None
    else:
        raw_city_data = raw_data
        imputed_city_data = imputed_data
        if predicted_data is not None:
            if predicted_data is not None:
                pred_t = predicted_data
        else:
            pred_t = None

    if len(imputed_city_data) == 0:
        print("region ", region, ' is not in admin level ', admin_label)
        return 0

    # transverse the matrix
    raw_products = [item for item in product_list if item != 'meb'] # remove meb for raw data
    raw_t = raw_city_data.melt(id_vars=['year_month'], value_vars=raw_products,
                               var_name='products', value_name=region)
    imp_t = imputed_city_data.melt(id_vars=['year_month'], value_vars=product_list,
                            var_name='products', value_name=region)
    if pred_t is not None:
        predicted_prodicts_without_meb = PREDICT_PRODUCTS.copy()
        if 'meb' in predicted_prodicts_without_meb:
            predicted_prodicts_without_meb.remove('meb')
        pred_t = pred_t.melt(id_vars=['year_month'], value_vars=predicted_prodicts_without_meb,
                             var_name='products', value_name=region)

    plot_data(raw_t, imp_t, region, 'products', admin_label, pred_t)
    return raw_t, imp_t, pred_t


def plot_by_product(choice, raw_data, imputed_data, predicted_data=None):
    """plot prices in diffrent regions of a specific product

    Args:
        choice (int): task choice
        raw_data (dictionary): raw data
        imputed_data (dictionary): imputed data
        predicted_data (dictionary, optional): predicted data. Defaults to None.
    Returns:
        bool: return 1 if succful processing
    """
    if choice in [1, 2]:
        products_list = ['meb'] + PRODUCTS_LABELS

    else:
        products_list = PREDICT_PRODUCTS
    admin_list = list(set(ADMIN_LOCATIONS) & set(imputed_data.keys()))
    for admin in admin_list:
        for product in products_list:
            if choice in [2, 3]:
                plot_data(raw_data[admin], imputed_data[admin],
                        product, admin, admin, predicted_data=predicted_data[admin])
            else:
                plot_data(raw_data[admin], imputed_data[admin],
                        product, admin, admin)
    return 1

def plot_by_city(choice, raw_data, imputed_data, predicted_data):
    """plot the prices of diffrent products for each region

    Args:
        choice (int): task choice
        raw_data (dictionary): raw data
        imputed_data (dictionary): imputed data
        predicted_data (dictionary, optional): predicted data. Defaults to None.
    Returns:
        bool: return 1 if succful processing
    """
    regions_list = PREDICT_CITIES
    product_list = PREDICT_PRODUCTS
    admin_list = list(set(ADMIN_LOCATIONS) & set(imputed_data.keys()))
    for admin in admin_list:
        if choice in [1, 2]:
            product_list = PRODUCTS_LABELS
            regions_list = ADMIN_LOCATIONS[admin]
        if admin == 'admin0_label':
            regions_list = ['Syria']
        if 'meb' in product_list:  # remove meb since it higher than other products
            product_list.remove('meb')

        for region in regions_list:
            if region != '':
                if choice in [2, 3]:
                    plot_product_prices_in_city(raw_data[admin], imputed_data[admin],
                                                admin, region, product_list, predicted_data[admin])
                else:
                    plot_product_prices_in_city(raw_data[admin], imputed_data[admin],
                                                admin, region, product_list, None)
    return 1


def visualization_conroler(choice, raw_data, imputed_data, predicted_data):
    """plot the processed data

    Args:
        choice (int): task choice
        raw_data (dictionary): raw data
        imputed_data (dictionary): imputed data
        predicted_data (dictionary, optional): predicted data. Defaults to None.
    Returns:
        bool: return 1 if succful processing
    """
    log.info("start plottng data by product")
    plot_by_product(choice, raw_data, imputed_data, predicted_data)
    log.info("start plottng data by region")
    plot_by_city(choice, raw_data, imputed_data, predicted_data)
    return 1
