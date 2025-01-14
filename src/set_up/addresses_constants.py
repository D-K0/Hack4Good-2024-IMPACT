#####################
# RAW DATA
#####################

# ADRS_RAW_DATA = 'C:\\Users\\gabri\\Desktop\\Hack4Good_24\\Branch_diana\\impact\\data\\raw\\dataframe_data.csv'
# or use:   './../../data/raw/dataframe_data.csv'
ADRS_RAW_DATA = './../data/raw/dataframe_data.csv'


####################
# IMPUTED DATA
####################

# where the imputation of the entire data store
ADRS_IMPUTED_ADMIN0 = './../data/processed/imputed_admin0_label_full.csv'
ADRS_IMPUTED_ADMIN1 = './../data/processed/imputed_admin1_label_full.csv'
ADRS_IMPUTED_ADMIN2 = './../data/processed/imputed_admin2_label_full.csv'
ADRS_IMPUTED_ADMIN3 = './../data/processed/imputed_admin3_label_full.csv'
ADRS_IMPUTED_ADMIN4 = './../data/processed/imputed_admin4_label_full.csv'
ADRS_IMPUTED = {'admin0_label' : ADRS_IMPUTED_ADMIN0,
                'admin1_label' : ADRS_IMPUTED_ADMIN1,
                'admin2_label' : ADRS_IMPUTED_ADMIN2, 
                'admin3_label' : ADRS_IMPUTED_ADMIN3,
                'admin4_label' : ADRS_IMPUTED_ADMIN4}

#######################
# EXPORT DIR
######################

# unix time folder value
TIME_FOLDER = '000000000'

# ADRS_IMPORT_MEB_QUANTITY = './../data/raw/dataframe_SYR.csv' # TODO: automate quantity
ADRS_EXPORT_DIR = './../data/processed/'
ADRS_DIR_PLOT = './../data/plot/'