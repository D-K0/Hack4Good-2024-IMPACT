'''
    file description
'''
import warnings
import pandas as pd
import numpy as np
from modeling_permutation.local_regression import perform_local_regression_imputation
from modeling_permutation.finding_nearest_cities import find_nearest_cities
from modeling_permutation.global_regression import perform_global_regression_imputation
from modeling_permutation.arima_imputation import arima_imputation_fn
import logging
from set_up.labels import ADMIN_1_LABELS

log = logging.getLogger(__name__)  # Logger for this module


def create_admin1_dataset(admin_raw_df, admin_label):

    """
    This function creates a dataset that exclusively covers admin level 1 instances. It fills all NaN values using data imputation techniques that are listed in the documentation.

    Input: A dataset that has been preprocessed by the `raw_admin_dataset_creator()` with respect to "admin1_level." This means it contains a date column and the admin columns that encode all locations belonging to admin level 1. Additionally, all dates are encoded in the date format, and missing values are represented as NaN. Outliers should have already been removed.
    """
    warning_supressed_flag = False

        # Creating a copy of df to avoid modifying the original input
    df = admin_raw_df.copy()

    admin_1_locations = ADMIN_1_LABELS
    price_columns = [col for col in df.columns if col not in ["year_month", admin_label]]

    number_of_geo_imputation_runs = 2
    


    ##############################################################################################################

    #performing local regression:

    #iterate through all admin location and prices
    for ad in admin_1_locations:
        for price in price_columns:

            #Generate a one-column DataFrame that is ready to be analyzed.
            sinlge_admin_level_df = df[df[admin_label]== ad ]
            single_good_admin = sinlge_admin_level_df[price]
            single_good_admin = single_good_admin.reset_index().drop(columns = ["index"])

            #perform local regression and impute NaN values directly in single_good_admin
            perform_local_regression_imputation(single_good_admin)
            
            # Find the indices of the rows in target dataframe df where admin_level corresponds to the currently used one
            new_indices = df[df[admin_label] == ad].index
            
            #replace imputed NaN values in the target dataframe df
            df.loc[new_indices, price] = single_good_admin[price].values


    ##############################################################################################################
    # Perform geographic imputation for admin level 1
    # For each NaN value, the closest other admin level 1 locations are searched to see if they have a non-NaN value.
    # If they do, the average of the nearest cities is used.


    # Get nearest locations for each admin_1 location
    nearest_locations = find_nearest_cities(admin_1_locations, n = 4)  # returns a dictionary

    #Geo location is perform several times 
    for runs in range(number_of_geo_imputation_runs):
   
        # Finde nan indices in df
        for index, row in df.iterrows():
            for col in df.columns:
                if pd.isna(row[col]):  # check if it is nan value     
                    
                    current_location = df.iloc[index][admin_label]
                    current_date = df.iloc[index]["year_month"]
                    neighbors = nearest_locations[current_location]
                    
                    nearest_locations_values = []
                    
                    #generate average over neighbors
                    for i in range(len(neighbors)):
                        
                        #find one element dataframe with the desired value
                        filtered_df = df[   
                                (df['year_month'] == current_date) &  # Überprüft, ob das Datum "2015-03" ist
                                (df[admin_label] == neighbors[i])  # Überprüft, ob der admin_level "Aleppo" ist
                            ][col]
                        
                        nearest_locations_values.append(filtered_df)                

                    #take mean (consider nan values of neigbors here)
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=RuntimeWarning, message="Mean of empty slice")
                        if not warning_supressed_flag:
                            log.info("np.nanmean(nearest_locations_values) triggers a \"RuntimeWarning: Mean of empty slice\" that as been supressed")
                            warning_supressed_flag = True
                        average_value = np.nanmean(nearest_locations_values)

                    #replace nan value with derived average price
                    df.loc[index, col] = average_value


    #############################################################################################################
    # performing global regression:

    #iterate through all admin locations and prices
    for ad in admin_1_locations:
        for price in price_columns:
            
            
            #Generate a one-column DataFrame that is ready to be analyzed
            sinlge_admin_level_df = df[df[admin_label]== ad ]
            single_good_admin = sinlge_admin_level_df[price]
            single_good_admin = single_good_admin.reset_index().drop(columns = ["index"])

            #perform global regression
            perform_global_regression_imputation(single_good_admin, dim = 3) #This function performs a polynomial regression of a specified dimension on the entire dataset and replaces all remaining NaN values with predictions from the regression
            
            # Find the indices of the rows in target dataframe df where admin_level corresponds to the currently used one
            new_indices = df[df[admin_label] == ad].index
            

            #replace imputed NaN values in the target dataframe df
            df.loc[new_indices, price] = single_good_admin[price].values

################ #arima
    df = arima_imputation_fn(df_cleaned = df, admin_label=admin_label , nan_df = admin_raw_df)
    
      
    return df


        

                