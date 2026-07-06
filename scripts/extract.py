import pandas as pd
from typing import Dict
from pathlib import Path

from scripts.config import DATA_RAW_DIR, DATA_ERP_CRM_DIR, DATASETS
from scripts.logger import get_logger

logger = get_logger(__name__)

def load_data() -> Dict[str, pd.DataFrame]:
    """
    Loads all raw CSV files into pandas DataFrames.
    
    Returns:
        Dict[str, pd.DataFrame]: A dictionary mapping dataset names to their DataFrames.
    """
    data_frames = {}
    
    for name, config in DATASETS.items():
        file_path = DATA_RAW_DIR / config["filename"]
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            continue
            
        try:
            logger.info(f"Loading {name} dataset from {file_path}")
            df = pd.read_csv(file_path, low_memory=False)
            logger.info(f"Successfully loaded {name} dataset. Shape: {df.shape}")
            data_frames[name] = df
        except Exception as e:
            logger.error(f"Error loading {name} dataset: {str(e)}")

    # Load ERP Datasets
    erp_files = {
        'erp_inventory': 'Inventory.csv',
        'erp_marketing': 'Marketing_Campaign.csv',
        'erp_customer_profile': 'Customer_Profile.csv',
        'erp_product_master': 'Product_Master.csv',
        'erp_warehouse': 'Warehouse.csv'
    }
    
    for name, filename in erp_files.items():
        file_path = DATA_ERP_CRM_DIR / filename
        if file_path.exists():
            try:
                logger.info(f"Loading ERP dataset {name} from {file_path}")
                df = pd.read_csv(file_path, low_memory=False)
                logger.info(f"Successfully loaded {name} dataset. Shape: {df.shape}")
                data_frames[name] = df
            except Exception as e:
                logger.error(f"Error loading {name} dataset: {str(e)}")
        else:
            logger.warning(f"ERP dataset not found: {file_path}")

    return data_frames
