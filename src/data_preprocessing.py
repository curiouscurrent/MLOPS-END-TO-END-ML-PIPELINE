import os 
import logging 
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import string
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

# Ensure the "logs" directory exists
log_dir = 'logs'
os.makedirs(log_dir,exist_ok=True)

# Setting up logger
logger = logging.getLogger('data_prerocessing')
logger.setLevel('DEBUG')

# Console handler for printing logs to console
console_handler = logging.StreamHandler()
console_handler.setLevel('DEBUG')

# File handler for saving logs to a file
log_file_path = os.path.join(log_dir, 'data_preprocessing.log')
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel('DEBUG')

# set the formatter for the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# add both handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

# Data preprocessing functions
# Transform the text column and encode the target column
def transform_text(text):
    """
    Transforms the input text by converting it to lowercase, tokenizing,
    removing stopwords and punctuation, and applying stemming.
    
    :param text: provide the text column as input
    """
    ps = PorterStemmer()
    # Convert to lowercase
    text = text.lower()
    # tokenise the text
    text = nltk.word_tokenize(text)
    # remove non alphanumeric tokens
    text = [word for word in text if word.isalnum()]
    # remove stopwords and punctuation
    text = [word for word in text if word not in stopwords.words('english') and word not in string.punctuation]
    # apply stemming
    text = [ps.stem(word) for word in text]
    # join the tokens back into a single string with a space separator
    return " ".join(text)

def preprocess_df(df, text_column='text', target_column='target'):
    """
    Preprocesses the Dataframe by encoding the target column, removing duplicates and transforming the text column.

    
    :param df: input dataframe 
    :param text_column: text column of the dataframe
    :param target_column: target column of the dataframe
    """
    try:
        logger.debug('Starting preprocessing for Dataframe')
        # Encode the target column
        encoder = LabelEncoder()
        df[target_column] = encoder.fit_transform(df[target_column])
        logger.debug('Target column encoded successfully')

        # Remove duplicate rows
        df = df.drop_duplicates(keep='first')
        logger.debug('Duplicate rows removed successfully')

        # Apply text transformation to the specified text column
        df.loc[:,text_column] = df[text_column].apply(transform_text)
        logger.debug('Text column transformed successfully')
        return df
    except KeyError as e:
        logger.error('Column not found %s', e)
        raise
    except Exception as e:
        logger.error('Unexpected error during text normalization: %s',e)
        raise

def main(text_column='text', target_column='target'):
    """
    Main function to load raw data, preprocess it, and save the processed data.

    
    :param text_column: the text column to be transformed
    :param target_column: the target column to be encoded
    """
    try:
        # Fetch the train and test data from data/raw
        train_data = pd.read_csv('./data/raw/train.csv')
        test_data = pd.read_csv('./data/raw/test.csv')
        logger.debug('Data loaded successfully')

        # Transform the data
        train_preprocessed_data = preprocess_df(train_data, text_column, target_column)
        logger.debug('Training data preprocessed successfully')
        test_preprocessed_data = preprocess_df(test_data, text_column, target_column)
        logger.debug('Testing data preprocessed successfully')

        # Save the data inside data/interim
        data_path = os.path.join('./data', 'interim')
        os.makedirs(data_path, exist_ok=True)

        train_preprocessed_data.to_csv(os.path.join(data_path, 'train_preprocessed.csv'),index=False)
        test_preprocessed_data.to_csv(os.path.join(data_path, 'test_preprocessed.csv'), index=False)

        logger.debug('Preprocessed data saved to %s', data_path)
    except FileNotFoundError as e:
        logger.error('File not found : %s', e)
    except pd.errors.EmptyDataError as e:
        logger.error('No data : %s', e)
    except Exception as e:
        logger.error('Failed to complete the data preprocessing process : %s', e)
        print(f"Error : {e}")

if __name__ == '__main__':
    main()