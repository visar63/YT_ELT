from importlib.resources import path
import json
from datetime import date, timedelta
import logging

# set logging level to info

logger = logging.getLogger(__name__) # Set up a logger for this module
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

def load_data(days_ago: int = 1) -> dict:
    filename = f"video_details_{date.today() - timedelta(days=days_ago)}.json"  # Create a filename with the current date
    file_path = f"./data/{filename}"  # Create a file path with the current date


    logger.info(f"Loading data from {filename}")  # Log a message indicating the file being loaded
    try:
        with open(file_path, 'r', encoding='utf-8') as file:  # Open the JSON file for reading
            data = json.load(file)  # Load the JSON data from the file
            logger.info(f"Successfully loaded data from {filename}")
            return data  # Return the loaded data
        
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")  # Log error message if file is not found
        return {}  # Return an empty dictionary if the file does not exist
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {filename}")  # Log error message if there is an issue decoding the JSON
        return {}  # Return an empty dictionary if there is an error decoding the JSON
    except Exception as e:
        logger.error(f"An error occurred while loading data from {filename}: {e}")  # Log any other exceptions
        return {}  # Return an empty dictionary if an error occurs


# load_path()  # Call the load_path function to load the data from the JSON file