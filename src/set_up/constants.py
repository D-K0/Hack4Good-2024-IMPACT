from set_up.labels import RAW_MIN_DATE, RAW_MAX_DATE, ALL_ADMIN_LOCATIONS, ALL_PRODUCTS_LABELS, ALL_PRODUCT_MEB_QUANTITIES
from set_up.addresses_constants import ADRS_RAW_DATA, ADRS_IMPUTED
##################################################################################
#                                                             
#   YOU MAY CHANGE ANY OF THE FOLLOWING CONSTANTS AS NEEDED
#
##################################################################################


#################################
#       Imputation
#################################

# imputation admin
ADMIN_LOCATIONS = {'admin0_label' : ALL_ADMIN_LOCATIONS['admin0_label'],
                   'admin1_label' : ALL_ADMIN_LOCATIONS['admin1_label'],
                   'admin2_label' : ALL_ADMIN_LOCATIONS['admin2_label'],
                   'admin3_label' : ALL_ADMIN_LOCATIONS['admin3_label']}

# imputation products
PRODUCTS_LABELS = ALL_PRODUCTS_LABELS
# ALL_PRODUCTS_LABELS = ['bread_price', 'bulgur_price', 'chicken_meat_price', 'cucumber_price',
#                    'egg_price', 'kerosene_manually_refined_price','laundry_soap_bar_price', 
#                    'lentil_price', 'onion_price', 'potato_price', 'rice_price', 'salt_price', 
#                    'sanitary_pad_price', 'soap_price', 'sugar_price', 'tomato_paste_price', 
#                    'tomato_price', 'toothpaste_price', 'vegetable_oil_price']

#################################
#       Prediciton
#################################

# prediciton admin
PREDICT_ADMIN = 'admin1_label'
# prediction cities
PREDICT_CITIES = ['Aleppo']
# prediciton products
PREDICT_PRODUCTS = ['bulgur_price']
# - min month
CHOSEN_MIN_DATE = '2016-05' # Do not go before 2016-05' as data was there pretty messy
# - max month
CHOSEN_MAX_DATE = '2024-09'



##################################################################################
#                                                             
#   DO NOT CHANGE UNLESS YOU ARE A DEVELOPER
#
##################################################################################
# import address
ADRS_IMPORT = ADRS_RAW_DATA

MIN_DATE = CHOSEN_MIN_DATE
MAX_DATE = CHOSEN_MAX_DATE

# - predicted number of months
N_MONTHS = 6

CHOICE = 0

# Dictionary mapping product names to their respective quantities of the MEB
# it get filtered in calculate_meb. Could be done in interface instead
PRODUCT_MEB_QUANTITIES  = ALL_PRODUCT_MEB_QUANTITIES


