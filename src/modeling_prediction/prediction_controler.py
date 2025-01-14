from set_up.constants import PREDICT_ADMIN
# from preprocessing.prim_imputations import basic_impute_data
from modeling_prediction.model import model_controler
import logging

log = logging.getLogger(__name__)  # Logger for this module


def prediction_controler(imputed_dataframe, admin_label, cities, products, n_months):
    """
    Predict the prices of the products in the cities for the next n_months
    :param imputed_dataframe: the imputed data
    :param admin_level: the admin level to predict
    :param cities: the cities to predict
    :param products: the products to predict
    :param n_months: the number of months to predict
    :return: the prediction
    """
    # Check if the product "meb" is in the list and if the list contains more than one product
    if "meb" in products and len(products) > 1:
        # If both conditions are true, raise a ValueError with a descriptive error message
        raise ValueError(
            "Please note that when 'meb' shall be predicted, no other products should be predicted in the same run. "
            "Please go to the setup folder and change the list 'PREDICT_PRODUCTS' in the 'constants' file so that it "
            "only contains 'meb' or any combination of other products."
        )
    
    log.info(f"Predicting the prices of the products in the cities for the next {n_months}")
    # Get the data for the admin level, cities and products
    # seasonal = 0 (ARIMA), 1 (S-ARIMA), any other integer (GARCH)... GARCH is the better model
    predicted_data = model_controler(imputed_dataframe, admin_label, cities, products, n_steps = n_months, seasonal = 2)
    predicted_data['year_month'] = predicted_data['year_month'].dt.strftime('%Y-%m') # do we need this line

    return predicted_data
