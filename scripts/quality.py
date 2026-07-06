import json
from pathlib import Path
from typing import Dict
import pandas as pd
from datetime import datetime

from scripts.config import REPORTS_DIR
from scripts.logger import get_logger

logger = get_logger(__name__)

def generate_quality_report(raw_data: Dict[str, pd.DataFrame], cleaned_data: Dict[str, pd.DataFrame]) -> None:
    """
    Generate a Data Quality Report for the final Data Warehouse Star Schema.
    """
    report = {
        "generated_at": datetime.now().isoformat(),
        "star_schema_tables": {}
    }
    
    for name, df in cleaned_data.items():
        missing_counts = df.isnull().sum().to_dict()
        missing_percentages = {col: (val / len(df)) * 100 if len(df) > 0 else 0 
                             for col, val in missing_counts.items()}
        
        dataset_report = {
            "rows": len(df),
            "columns": len(df.columns),
            "missing_values": missing_counts,
            "missing_percentage": missing_percentages
        }
        
        report["star_schema_tables"][name] = dataset_report
        
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORTS_DIR / f"dwh_quality_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=4)
        
    logger.info(f"Data quality report generated at: {report_file}")
