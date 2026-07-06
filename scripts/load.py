import pandas as pd
from typing import Dict

from scripts.config import DATA_WAREHOUSE_DIR
from scripts.logger import get_logger

logger = get_logger(__name__)

def save_data(data_frames: Dict[str, pd.DataFrame]) -> None:
    """
    Save the cleaned pandas DataFrames to the processed directory as CSV files.
    """
    for name, df in data_frames.items():
        file_path = DATA_WAREHOUSE_DIR / f"{name}.csv"
        
        try:
            logger.info(f"Saving cleaned {name} dataset to {file_path}")
            # index=False avoids writing row numbers as a column
            df.to_csv(file_path, index=False)
            logger.info(f"Successfully saved {name}")
        except Exception as e:
            logger.error(f"Error saving {name} dataset: {str(e)}")
