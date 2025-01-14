'''
    file discription
'''
# import pandas as pd
import numpy as np
import numpy.polynomial.polynomial as Polynomial



def perform_local_regression_imputation(df, one_way_window=8):

    """
    This function performs local regression on a given DataFrame. 
    It utilizes the `local_regression_lists()` function, which returns a list of lists, each containing an interval of indexes. A polynomial regression is performed around these indexes, and any existing NaN values within the interval are recalculated.

    Input: 
        A pandas DataFrame with a single column indexed from 0 to ... (indicating the range of data).

    Output: 
        The function does not return a value; instead, it directly modifies the provided DataFrame by updating the NaN values with the results of the local regression.
    """

    nan_indices = df[df.isna().any(axis=1)].index.tolist()
    regression_list = local_regression_lists(nan_indices, len(df), one_way_window)



    for i in range(len(regression_list)):


            # Here are the predefined indices
        indices_to_fit = regression_list[i]

        #print(indices_to_fit)
        
        # Filter the DataFrame to include only the relevant indices
        subset = df.loc[indices_to_fit]

        # Remove NaN values and create x and y for the regression
        subset_cleaned = subset.dropna()
        x = subset_cleaned.index.astype(float)  # Convert the index to float
        y = subset_cleaned.values  # Extract the values for y

        # Identify the indices where NaN values are present in the first column
        nan_indices = subset[subset[subset.columns[0]].isna()].index
   
        # Fit a polynomial model of degree 2
        coefs = Polynomial.polyfit(x, y, 3)  # Calculate the coefficients

        coefs = np.array(coefs).flatten()  # Flatten the coefficients array
        # Create a function for prediction based on the model
        polynomial = Polynomial.Polynomial(coefs)

        # Predict values for the original indices where NaN values were found
        predicted_values = polynomial(nan_indices)  # Prediction for the x-values

        
       # Set the predicted values in the DataFrame at the appropriate positions
        df.loc[nan_indices, df.columns[0]] = predicted_values 



def local_regression_lists(nan_indices_raw, ts_length , one_way_window = 8):

    """
    This function receives a list of indexes, each representing a NaN value in a time series. 
    For each index, a one-way window is applied in both directions to determine a new interval in which the NaN values reside. 
    The function ensures that the intervals do not overlap; if they do, they are merged into a single interval. 
    Additionally, intervals are constrained to contain no negative values and no values exceeding the maximum time series length defined by `ts_length`.

    Furthermore, all resulting intervals are checked to ensure that no interval contains less than 40% of its length as valid values (i.e., no more than 40% of the interval is allowed to be NaN values).

    Inputs:
        nan_indices_raw: A list of indexes corresponding to NaN values in the time series.
        ts_length: An integer that determines the maximum allowable length of the time series.
        one_way_window: An integer representing half the overall window size that defines the newly created interval.

    Outputs:
        A list of lists, where each sublist contains a new sorted interval. For example, list_of_lists = [[1, 2, 3, 4, 5], [9, 10, 11, 12, 13, 14, 15], ...].
    """

    list_of_lists = []
    counter = 0
    counter_list = 0

    #remove indices if they are toc close to the beginning or to the end 
    nan_indices = [
        index for index in nan_indices_raw 
        if index >= 1+ one_way_window and index < ts_length - one_way_window -1
    ]

    #generate new intervals
    for i in (nan_indices):
        
        # generate interval
        new_list = list(range(i - one_way_window, i + one_way_window + 1))


        if counter >0:
            
            #check if the some intervals overlap
            if (nan_indices[counter]-one_way_window) < list_of_lists[counter_list-1][-1]:
                
                #merge overlapping intervalls
                list_of_lists[counter_list-1] = list(set(list_of_lists[counter_list-1] + new_list))
                counter += 1
                continue
                    
            
        list_of_lists.append(new_list)

        counter += 1
        counter_list += 1

    #check if end and starting elements of new_list contains a non nan. If it does, neglect this new_list
    list_of_lists = [
    lst for lst in list_of_lists
    if lst and (lst[0] not in nan_indices_raw or lst[1] not in nan_indices_raw) and (lst[-1] not in nan_indices_raw and lst[-2] not in nan_indices_raw)
        ]

    #make sure that there is enough known data for each regression and not too much NaN
    delete_counter = 0
    for i in range(len(list_of_lists)):
     
        #check for matching indices
        common_elements = set(nan_indices_raw).intersection(set(list_of_lists[i-delete_counter]))
        count_common = len(common_elements)

        if count_common > int(0.6*len(list_of_lists[i-delete_counter])):
            list_of_lists.pop(i-delete_counter)  #remove list if too many nans are available
            delete_counter += 1

    return(list_of_lists)

    

