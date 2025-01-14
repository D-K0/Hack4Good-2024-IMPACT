"""
    Program that give a csv file will either predict or impute data (or both)
"""
import logging
from collections import defaultdict
import warnings

from set_up.interface import interface
from preprocessing.data_loading import data_loading
from preprocessing.preprocessong_controler import preprocessong_controler as preprocessing
from modeling_permutation.imputation_controler import imput_controler as imputation
from modeling_prediction.prediction_controler import prediction_controler as prediction
from results.data_export import export_controler as export
from results.visualization import visualization_conroler as visualization

from set_up.constants import ADRS_IMPORT, \
    MIN_DATE, MAX_DATE, N_MONTHS, \
        ADMIN_LOCATIONS, PREDICT_ADMIN, \
            PREDICT_CITIES, PREDICT_PRODUCTS, \
                ADRS_IMPUTED


warnings.filterwarnings('ignore')
# set up a log system
logging.basicConfig(
    format="{asctime} - {filename} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO  # Set logging level to INFO
)
log = logging.getLogger(__name__) # instantiate a Logger


if __name__ == "__main__":
    log.info("Started the program")

    log.info("Runs interface stage")
    choice = interface()
    if choice == 0:
        print("program closed without processing.")
        log.info("program closed without processing.")
        exit()

    log.info("Runs data loading stage")
    unprocessed_data = data_loading(ADRS_IMPORT)

    log.info("Runs preprocessing stage")
    outlierless_data, admin_raw_data = preprocessing(unprocessed_data,
                                                     min_date=MIN_DATE, max_date=MAX_DATE)

    log.info("Runs Imputation stage")
    imputed_data = {}
    if choice in {1, 2}:
        data_wihtout_meb, imputed_data = imputation(outlierless_data, admin_raw_data)
    elif choice == 3:
        imputed_data[PREDICT_ADMIN] = data_loading(ADRS_IMPUTED[PREDICT_ADMIN])
    else:
        raise ValueError("no imputated data was loaded")

    predicted_data = defaultdict(lambda: None) #m makes it so any other key return None
    if choice in {2, 3}:
        log.info("Run prediction stage")
        predicted_data[PREDICT_ADMIN] = prediction(imputed_data[PREDICT_ADMIN], PREDICT_ADMIN,\
                                                         PREDICT_CITIES, PREDICT_PRODUCTS, N_MONTHS)

    log.info("Runs Export stage")
    export(choice, imputed_data, predicted_data)

    log.info("Runs visualization stage")
    visualization(choice, admin_raw_data, imputed_data, predicted_data)

    log.info("Program completed")
