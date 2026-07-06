import sys
from pathlib import Path

# Add project root to python path if not running from root
sys.path.append(str(Path(__file__).parent.parent))

from scripts.extract import load_data
from scripts.transform import transform_data
from scripts.quality import generate_quality_report
from scripts.load import save_data
from scripts.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Starting Olist ETL Pipeline")
    
    # Extract
    logger.info("--- EXTRACT PHASE ---")
    raw_data = load_data()
    
    if not raw_data:
        logger.error("No data loaded. Pipeline aborted.")
        return
        
    # Transform
    logger.info("--- TRANSFORM PHASE ---")
    cleaned_data = transform_data(raw_data)
    
    # Data Quality Report
    logger.info("--- QUALITY REPORT PHASE ---")
    generate_quality_report(raw_data, cleaned_data)
    
    # Load
    logger.info("--- LOAD PHASE ---")
    save_data(cleaned_data)
    
    logger.info("Olist ETL Pipeline Completed Successfully")

if __name__ == "__main__":
    main()
