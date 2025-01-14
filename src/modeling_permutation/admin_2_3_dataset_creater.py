'''
    file description
'''

import sys

import pandas as pd

from modeling_permutation.local_regression import perform_local_regression_imputation

def create_admin_2_3_dataset(admin_raw_df, admin_label, upper_admin_cleaned_df, all_admin_df):

    """
        This function performs data imputation and cleans the preprocessed dataframe for a specific administrative level (only levels 2 or 3),
        removing all NaN values. See documentation for technical details

        Parameters:
            admin_raw_df (pd.DataFrame): A Pandas dataframe produced by the function `generate_raw_admin_data()`. 
                                        This dataframe contains columns for prices, a date column, and an "admin_level" 
                                        column that encodes all possible locations at the specified admin level.
                                        The "admin_level" column corresponds to the desired administrative level.
            
            upper_admin_cleaned_df (pd.DataFrame): A Pandas dataframe that belongs to the upper administrative level 
                                                (e.g., if calculating for admin level 2, then `upper_admin_cleaned_df` 
                                                refers to admin_level=1). This is a cleaned dataframe without any NaN values.
            
            all_admin_df (pd.DataFrame): A dataframe containing information about all admin levels to assess their relationships.
                                        This dataframe may contain NaN values, as only the "admin_level" columns are analyzed.
                                        It may be the dataset used as input for `generate_raw_admin_data()`.
        
            admin_label (str): A string that indicates the admin level of the provided `admin_raw_df`.
                                    Allowed values are: 'admin2_label' or 'admin3_label'. For admin level 1,
                                    please use the designated function.
        
        Returns:
            pd.DataFrame: A Pandas dataframe that has been cleaned of all NaN values.
    """

     # Check if the provided admin level is "admin1_label"
    if admin_label == "admin1_label":
        sys.exit("Error: This function is not meant to process the admin level 1 dataset. "
              "Please use the designated function for admin level 1.")        

    # Determine the higher admin level based on the input admin level
    elif admin_label == "admin2_label":
        higher_admin_level_string = "admin1_label"
       
    elif admin_label == "admin3_label":
        higher_admin_level_string = "admin2_label"
         

    # Handle cases where the admin_label does not match expected values
    else:
        sys.exit("Error: The input argument `admin_level_string` is invalid. "
              "Allowed values are: 'admin2_label' or 'admin3_label'.")

       
    
        
    # remove " " admin names
    admin_raw_df = admin_raw_df[admin_raw_df[admin_label] != " "]
    admin_raw_df = admin_raw_df.reset_index(drop=True)

    # Find all unique values in the 'admin_level' column
    unique_admin_levels = admin_raw_df[admin_label].unique()
    # This summarizes the specific admin locations into a single list
    admin_location_list = unique_admin_levels.tolist()
    if " " in admin_location_list:
        admin_location_list.remove(" ")

    #create a list with all price column names
    price_columns = [col for col in admin_raw_df.columns if col not in ["year_month", admin_label]]

    # Create a dictionary that assigns each admin location its corresponding location in the admin level above
    corresponding_higher_admin_location = {}
    for loc in admin_location_list:
        if loc == " ":
            continue
        test = all_admin_df.loc[all_admin_df[admin_label]==loc]
        corresponding_higher_admin_location[loc] = test[higher_admin_level_string].iloc[0]


    #performing local regression:
    #iterate through all admin location and prices
    for ad in admin_location_list:
        for price in price_columns:            

            #Generate a one-column DataFrame that is ready to be analyzed.
            sinlge_admin_level_df = admin_raw_df[admin_raw_df[admin_label]== ad ]
            single_good_admin = sinlge_admin_level_df[price]
            single_good_admin = single_good_admin.reset_index().drop(columns = ["index"])

            #perform local regression 2 times and impute NaN values directly within single_good_admin
            perform_local_regression_imputation(single_good_admin,one_way_window = 5)
            perform_local_regression_imputation(single_good_admin,one_way_window=8)
          
            
            # Find the indices of the rows in target dataframe df where admin_level corresponds to the currently used one
            new_indices = admin_raw_df[admin_raw_df[admin_label] == ad].index
            
            #replace imputed NaN values in the target dataframe df
            admin_raw_df.loc[new_indices, price] = single_good_admin[price].values



    # Perform geographic imputation:
    # For each NaN value, the locations the admin level above is addressed an its not nan value is used to impute the nan 
    
    # Finde nan indices in df
    for index, row in admin_raw_df.iterrows():
        for col in admin_raw_df.columns:
            if pd.isna(row[col]):  # check if it is nan value     
                
                current_location = admin_raw_df.iloc[index][admin_label]
                current_date = admin_raw_df.iloc[index]["year_month"]
                
                #use non nan value of upper admin level
                nearest_locations_values = corresponding_higher_admin_location[current_location]          

                #find one element dataframe with the desired value
                filtered_df = upper_admin_cleaned_df[   
                        (upper_admin_cleaned_df['year_month'] == current_date) &  
                        (upper_admin_cleaned_df[higher_admin_level_string]== nearest_locations_values)][col]
                
                 #replace nan value with derived average price
                admin_raw_df.loc[index, col] = filtered_df.iloc[0]



    return admin_raw_df

    
