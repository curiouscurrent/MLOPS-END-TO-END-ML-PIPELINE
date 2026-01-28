import pandas as pd
import os
from sklearn.model_selection import train_test_split
import logging

# Ensure the logs directory exists
# this directory will save all the logs
os.makedirs('logs',exist_ok=True) # if the directory does not exist in the project folder create it else skip it

# create a Logger class from the logging module

# logging is a py file which contains the getLogger method, 
# which returns the object of Logger class that is stored in logger 
logger = logging.getLogger('data_ingestion')
logger.setLevel('DEBUG')

# now create a console handler to print the logs on the console using the StreamHandler class
console_handler = logging.StreamHandler()
console_handler.setLevel('DEBUG')

# now create a file handler to save the logs in a file using the FileHandler class
log_file_path = os.path.join('logs', 'data_ingestion.log')
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel('DEBUG')

# now create a formatter to format the logs 
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# now add this formatter while printing the logs on console and saving the logs in a file
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# now add both the handlers to the logger 
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# do not propagate the logs to the root logger to prevent duplicate logs since we have custom handlers
logger.propagate = False

# Load data from url
def load_data(data_url : str) -> pd.DataFrame:
    """
    Load data from a CSV file located at the given URL.
    
    :param data_url: take input from user in the form of url
    :type data_url: str
    :return: return the dataframe loaded from the url
    :rtype: DataFrame
    """
    try:
        df = pd.read_csv(data_url)
        logger.debug('Data loaded from %s', data_url)
        return df
    except pd.errors.ParserError as e:
        # printing an object triggers the __str__ magic method of the object
        logger.error('Failed to parse the CSV file : %s', e)
        raise
    except Exception as e : 
        logger.error('Unexpected error occured while loadin the data : %s',e)
        raise

# Preprocess data
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the data
    
    :param df: Input dataframe
    :type df: pd.DataFrame
    :return: Preprocessed dataframe
    :rtype: DataFrame
    """
    try:
        df.drop(columns=['Unnamed: 2','Unnamed: 3','Unnamed: 4'],inplace=True)
        df.rename(columns={'v1':'target','v2':'text'},inplace=True)
        logger.debug('Data preprocessing completed')
        return df
    except KeyError as e:
        # raise an exception when columns such as unnamed:2, unnamed:3, unnamed:4 are not present in the dataframe
        # raise an exception when columns such as v1 and v2 are not present in the dataframe
        logger.error('Missing expected columnns in the dataframe: %s',e)
        raise
    except Exception as e:
        logger.error('Unexpected error during preprocessing: %s',e)
        raise

# Save data 
def save_data(train_data: pd.DataFrame, test_data:pd.DataFrame,data_path: str) -> None:
    """
    Docstring for save_data
    
    :param train_data: The training data 
    :type train_data: pd.DataFrame
    :param test_data: The testing data
    :type test_data: pd.DataFrame
    :param data_path: The path where train and test data will be saved under. 
    :type data_path: str
    """
    try:
        raw_data_path = os.path.join(data_path, 'raw')
        os.makedirs(raw_data_path, exist_ok=True)
        train_data.to_csv(os.path.join(raw_data_path, 'train.csv'), index=False)
        test_data.to_csv(os.path.join(raw_data_path, 'test.csv'), index=False)
        logger.debug('Train and test data saved to %s', raw_data_path)
    except Exception as e:
        logger.error('Unexpected error while saving data: %s', e)
        raise

def main():
    try:
        test_size = 0.2
        data_path = "https://raw.githubusercontent.com/curiouscurrent/Datasets/refs/heads/main/spam.csv"
        df = load_data(data_url=data_path)
        final_data = preprocess_data(df)
        train_data,test_data  = train_test_split(final_data,test_size=test_size,random_state=2)
        save_data(train_data,test_data,data_path='./data')
    except Exception as e:
        logger.error('Failed to complete the data ingestion process: %s',e)
        print(f"Error : {e}")

if __name__ == "__main__":
    main()

