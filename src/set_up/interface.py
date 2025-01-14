"""
    run a short prompt to interact with the user to set up parameters
    and make sure the parameters are valid.
"""
import logging

from datetime import datetime
import os

import set_up.addresses_constants as ac
import set_up.constants as c
import set_up.labels as l

log = logging.getLogger(__name__)  # Logger for this module

def directory_exists(path: str) -> bool:
    """check if the directory exists

    Args:
        path (str): path that is checked

    Returns:
        bool: results of the check
    """
    return os.path.isdir(path)

def file_exists(path: str) -> bool:
    """check if the file exists

    Args:
        path (str): path that is checked

    Returns:
        bool: results of the check
    """
    return os.path.isfile(path)

def choice_eror_message(choice, options):
    """check wether the input is one of the options

    Args:
        choice: choice
        options (list): all possible choices that are valid

    Returns:
        bool: is choice a valid option?
    """
    if choice not in options:
        print("you choise is invalid. ")
        print("Please choose from the following options ", options, " . \n\n")
        return 1
    return 0

def set_a_in_set_b(set_a, set_b):
    """check if set A is in set B

    Args:
        setA (set): <-
        setB (set): <-

    Returns:
        bool: result wether A is a subset of B
    """
    set_a = set(set_a)
    set_b = set(set_b)
    # Check if source_set is a subset of target_set
    return set_a.issubset(set_b)

def opening_text():
    """
        opening messages
    """
    print("~~~~~~~~~~~~~~~~~~~~~~~\n")
    print("Hello!")
    print("This is a program which can impute and predict information")
    print("based on pre-existing data.")


###############
# choice
###############

def get_task_type():
    """
        get the task to perform
        1: only imputation
        2: imputation followed by prediction
        3: only predicition
    """
    def choice_menu():
        print("press 1 for imputation without prediction.")
        print("press 2 for imputation with predicition.")
        print("press 3 for predicition without imputation.")
        print("press 0 to exit")
        choice = input("your choice = ")
        try:
            choice = int(choice)
        except Exception as exc:
            raise TypeError("Your choice is not an int") from exc
        print("your choice is ", choice)
        return choice

    while True:
        print("~~~~~~~~~~~~~~~~~~~~~~~\n")
        choice = choice_menu()
        if not choice_eror_message(choice, [0, 1, 2, 3]):
            break
    c.CHOICE = choice
    return choice

##################
# time period
##################


def set_pred_n_moths(max_date, raw_max_date):
    """set the number of months that are being predicted

    Args:
        max_date (String): <-
        raw_max_date (String): the max date in the original data file

    Returns:
        _type_: return the diffrence between the chosen max maonth the datas month
    """
    # Parse the dates
    year1, month1 = map(int, max_date.split('-'))
    year2, month2 = map(int, raw_max_date.split('-'))
    # Convert to total months
    total_months1 = year1 * 12 + month1
    total_months2 = year2 * 12 + month2
    if total_months1 - total_months2 < 0:
        raise ValueError("the defined max date is higher than raw max date")
    # Find the difference
    return total_months1 - total_months2

def get_time_frame(choice): # pylint: disable=too-many-statements
    """get the time frame over which teh data will be cropped and assessed

    Args:
        choice (int): task choice

    Returns:
        String: data min date
        String: data max date
    """
    raw_min_month, raw_max_month = l.RAW_MIN_DATE, l.RAW_MAX_DATE
    def is_valid_date_format(date_str):
        try:
            datetime.strptime(date_str, "%Y-%m")
            return True
        except ValueError:
            return False
    def date_in_range(date_str):
        try:
            # Check if the date is within the range
            return (
                datetime.strptime(raw_min_month, "%Y-%m") <=
                datetime.strptime(date_str, "%Y-%m") <=
                datetime.strptime(raw_max_month, "%Y-%m")
            )
        except ValueError:
            return False
    def date_in_order(min_date, max_date):
        try:
            # Check if the date is within the range
            return (
                datetime.strptime(min_date, "%Y-%m") <
                datetime.strptime(max_date, "%Y-%m")
            )
        except ValueError:
            return False

    def choose_min_month(min_date):
        if is_valid_date_format(min_date):
            return min_date

        while True:
            print("~~~~~~~~~~~~~~~~~~~~~~~\n")
            if not is_valid_date_format(min_date):
                print("your chosen min month is ", min_date)
                print("unfortunatly, it does not follow the format YYYY-MM.")
                print("please follow the correct format")
            else: break
            min_date = input("Please choose your min month of processed data (YYYY-MM) = ")
        return min_date

    def choose_max_month(max_date, min_date, choice):
        if is_valid_date_format(max_date) \
            and date_in_order(min_date, max_date):
            if (choice==1) == (date_in_range(max_date)):
                return c.CHOSEN_MAX_DATE
            if (choice==1) == (not date_in_range(max_date)):
                return l.RAW_MAX_DATE
            if (choice!=1) == (not date_in_range(max_date)):
                return c.CHOSEN_MAX_DATE
        while True:
            print("~~~~~~~~~~~~~~~~~~~~~~~\n")
            print("your chosen min month is ", max_date)
            if not is_valid_date_format(max_date):
                print("unfortunatly, it does not follow the format YYYY-MM.")
                print("nor is it 0, for chaning min month value,")
                print("please follow the correct format")
            else:
                if not date_in_order(min_date, max_date):
                    print("min date ",min_date," is larger than max date ", max_date)
                elif choice==1 and not date_in_range(max_date):
                    print("you have chosen to perfom data imputation.")
                    print("as such, max date can only be within the range of raw data.")
                elif choice>1 and not date_in_range(max_date):
                    print("you have chosen to perfom data prediction.")
                    print("as such, max date can only be greater then the range of raw data.")
                else:
                    break

            print("given your min date is: ", min_date)
            print("(If you choose to change min date press 0)")
            max_date = input("Please choose your max month of processed data (YYYY-MM) = ")
            if max_date == '0':
                min_date = choose_min_month('xxxx-xx')
        return max_date

    print("~~~~~~~~~~~~~~~~~~~~~~~\n")
    print("Provided the original data spans ", raw_min_month, " to ", raw_max_month)
    min_date, max_date = c.CHOSEN_MIN_DATE, c.CHOSEN_MAX_DATE
    print("Your current chosen min month to assess is: ", min_date)
    min_date = choose_min_month(min_date)
    print("Your current chosen max month to assess is: ", max_date)
    max_date = choose_max_month(max_date, min_date, choice)

    if not (date_in_range(min_date) or date_in_range(max_date)):
        while True:
            if date_in_range(min_date) or date_in_range(max_date):
                break
            print("the min date", min_date," is smaller than ", raw_min_month)
            print("the max date", max_date," is larger than ", raw_max_month)
            print("Please choose a diffrent date range where \
                   at least one of the date is in raw date range.")
            min_date = choose_min_month(min_date)
            max_date = choose_max_month(max_date, min_date, choice)
    print("\ndata will be processed from ", min_date, " to ", max_date)
    print("\nIf you wish to change these months please edit set_up/constant.py")

    if choice > 1:
        c.N_MONTHS = set_pred_n_moths(max_date, l.RAW_MAX_DATE)

    c.MIN_DATE = min_date
    c.MAX_DATE = max_date
    return min_date, max_date

##########################
# ADRESS
##########################

def set_import_address(choice):
    """set the address that will be used for import

    Args:
        choice (int): task choice
    """
    if choice in [1, 2, 3]:
        adrs = ac.ADRS_RAW_DATA
    else:
        raise ValueError("choice value is invalid")
    if file_exists(adrs):
        c.ADRS_IMPORT = adrs
    else:
        raise LookupError(f"Could not find the file adress {adrs}")

##########################
#    Program parameters
##########################

def large_param_check_validity(choice):
    """check if the program parameters are valid for the program

    Args:
        choice (int): task choice
    """
    if choice in [1, 2]:
        # imputation admin
        if not set_a_in_set_b(c.ADMIN_LOCATIONS, l.ALL_ADMIN_LOCATIONS):
            raise IndexError('one of the imputed admin labels is not in the original data')
        # imputation products
        if not set_a_in_set_b(c.PRODUCTS_LABELS, l.ALL_PRODUCTS_LABELS):
            raise IndexError('one of the permutation products is not the raw data')

    if choice > 1:
        # prediciton admin
        if c.PREDICT_ADMIN not in l.ALL_ADMIN_LOCATIONS:
            raise IndexError('The chosen predicition admin label is not in the original data')
        # prediction cities
        if c.PREDICT_ADMIN != 'admin0_label' \
            and not set_a_in_set_b(c.PREDICT_CITIES, l.ALL_ADMIN_LOCATIONS[c.PREDICT_ADMIN]):
            raise IndexError("One of the chosen predicition city is not in the raw data")
        # prediciton products
        if not set_a_in_set_b(c.PREDICT_PRODUCTS, ['meb'] + l.ALL_PRODUCTS_LABELS):
            raise IndexError("One of the chosen predicition products is not in the raw data")


def all_param_print(choice):
    """print the parameters that will be used in the program

    Args:
        choice (int): task choice

    Returns:
        int: choice
    """
    print("\n\n ~~~~~~~~~~~~~~~~~~~~~~~\n")
    print("The following are the parameters")
    print("which will be used when running the program.")
    print("to edit them change them in impact/set_up/constants.py")
    print("The parameters currently assessed are: \n")

    if choice == 1:
        print("choice = ", choice, ". Program will perform imputation without predicition")
    elif choice == 2:
        print("choice = ", choice, ". Program will perform imputation with predicition")
    elif choice == 3:
        print("choice = ", choice, ". Program will perform predicition without imputation")
    else:
        raise ValueError("choice is out of bounds")

    print("data will be taken from: ", c.ADRS_IMPORT)
    print("raw data is recorded from ", l.RAW_MIN_DATE, " to ", l.RAW_MAX_DATE)
    print("data will be processed from ", c.MIN_DATE, " to ", c.MAX_DATE)

    if choice in [1, 2]:
        print("The imputed admins are: ", \
              c.ADMIN_LOCATIONS.keys())
        print("The imputed products are : ", c.PRODUCTS_LABELS)
    if choice > 1:
        print("The amount of months that will be predicted are : ", c.N_MONTHS)
        print("The predicted admin is : ", c.PREDICT_ADMIN)
        print("The predicted citites within that admin are : ", c.PREDICT_CITIES)
        print("The predicted products are : ", c.PREDICT_PRODUCTS)

    print("\nIf you are wish to change one or more of these parameters,")
    print("press 0 to exit.")
    print("Otherwise, press any other key")
    satisfaction_flag = input("your choice = ")
    if satisfaction_flag == '0':
        return 0
    return choice

##############
# controler
#############3

def interface():
    """run a short prompt to interact with the user to set up parameters
    and make sure the parameters are valid.

    Returns:
        int: task choice
    """
    opening_text()
    choice = get_task_type()
    # exit program
    if choice == 0:
        return choice

    get_time_frame(choice)
    large_param_check_validity(choice)
    set_import_address(choice)
    choice = all_param_print(choice)
    if choice == 0:
        return choice
    return choice
