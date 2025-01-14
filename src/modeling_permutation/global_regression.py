'''
    file discription
'''

# import pandas as pd
import numpy as np
import numpy.polynomial.polynomial as Polynomial

def perform_global_regression_imputation(df, dim = 3):

    """
        This function performs a polynomial regression of a specified dimension on the entire dataset and replaces NaN values with predictions from the regression.

        Input: 
            A pandas DataFrame with a single column indexed from 0 to ... (indicating the range of data).

        Output: 
            The function does not return a value; instead, it directly modifies the provided DataFrame by updating the NaN values with the results of the polynomial regression.
    """

    # Remove NaN values from the DataFrame to prepare for regression
    subset_cleaned = df.dropna()  # Create a new DataFrame without NaN values
    x = subset_cleaned.index.astype(float)  # Convert the index (which represents the x-values) to float type
    y = subset_cleaned.values  # Extract the values from the cleaned DataFrame for the y-values

    # Check if there are enough data points for polynomial regression
    if len(x) < 6:  # Ensure there are at least 6 data points available
        print("Too few measurements available. This time series will not be imputed and NaN values remain.")
        return  # Exit the function if there are too few measurements

    # Identify the indices of the NaN values in the original DataFrame
    nan_indices = df.index[df.isna()[df.columns[0]]]  # Get the index positions of NaN values in the specified column

    # Fit a polynomial model of the specified degree (dim)
    coefs = Polynomial.polyfit(x, y, dim)  # Calculate the polynomial coefficients based on the cleaned data

    coefs = np.array(coefs).flatten()  # Flatten the coefficients array to ensure it's a 1D array
    # Create a polynomial function using the calculated coefficients
    polynomial = Polynomial.Polynomial(coefs)

    # Predict values for the indices in the original DataFrame where NaN values were found
    predicted_values = polynomial(nan_indices)  # Use the polynomial function to compute predicted y-values for NaN indices

    # Assign the predicted values back into the original DataFrame at the positions of the NaN values
    df.loc[nan_indices, df.columns[0]] = predicted_values  # Update the original DataFrame with the predicted values





