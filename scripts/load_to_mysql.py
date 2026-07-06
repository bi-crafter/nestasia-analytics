import pandas as pd
from sqlalchemy import create_engine
import getpass
from pathlib import Path
import sys

# Add project root to python path if not running from root
sys.path.append(str(Path(__file__).parent.parent))
from scripts.config import DATA_WAREHOUSE_DIR
from scripts.logger import get_logger

logger = get_logger(__name__)

def load_csv_to_mysql():
    """
    Reads the exported Star Schema CSV files and loads them into the MySQL data warehouse.
    """
    logger.info("Starting Data Load to MySQL...")
    
    # Get MySQL connection details
    print("Enter MySQL Connection Details:")
    user = input("Username (default 'root'): ") or 'root'
    password = getpass.getpass("Password: ")
    host = input("Host (default 'localhost'): ") or 'localhost'
    port = input("Port (default '3306'): ") or '3306'
    database = 'nestasia_dwh'
    
    try:
        # Create SQLAlchemy engine
        connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(connection_string)
        logger.info(f"Connected to MySQL Database: {database}")
    except Exception as e:
        logger.error(f"Failed to connect to MySQL: {str(e)}")
        return

    # Order matters for Foreign Key constraints!
    # Load Dimensions first, then Facts.
    tables_to_load = [
        # Dimensions
        "Dim_Date", "Dim_Geography", "Dim_Category", "Dim_Product", 
        "Dim_Customer", "Dim_Seller", "Dim_Warehouse", "Dim_Campaign", 
        "Dim_Payment", "Dim_Shipping",
        # Facts
        "Fact_Sales", "Fact_Inventory", "Fact_Marketing", "Fact_Returns", 
        "Fact_Reviews", "Fact_Payments", "Fact_Shipping"
    ]
    
    for table_name in tables_to_load:
        file_path = DATA_WAREHOUSE_DIR / f"{table_name}.csv"
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}, skipping {table_name}.")
            continue
            
        try:
            logger.info(f"Loading {table_name}...")
            # Chunking to handle large files efficiently
            chunk_size = 10000
            chunks = pd.read_csv(file_path, chunksize=chunk_size, low_memory=False)
            
            is_first_chunk = True
            for chunk in chunks:
                # We use if_exists='append' because the tables are already created with constraints in MySQL
                chunk.to_sql(name=table_name, con=engine, if_exists='append', index=False)
                
                if is_first_chunk:
                    is_first_chunk = False
                    
            logger.info(f"Successfully loaded {table_name}")
            
        except Exception as e:
            logger.error(f"Failed to load {table_name}: {str(e)}")

    logger.info("Data Load to MySQL Completed.")

if __name__ == "__main__":
    load_csv_to_mysql()
