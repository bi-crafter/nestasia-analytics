from pathlib import Path

# Base directories
BASE_DIR = Path("d:/nestasia")
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATA_ERP_CRM_DIR = BASE_DIR / "data" / "erp_crm"
DATA_WAREHOUSE_DIR = BASE_DIR / "data" / "warehouse_export"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for _dir in [DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_ERP_CRM_DIR, DATA_WAREHOUSE_DIR, LOGS_DIR, REPORTS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

# Datasets configurations
DATASETS = {
    "customers": {
        "filename": "olist_customers_dataset.csv",
        "primary_key": ["customer_id"],
        "date_columns": []
    },
    "geolocation": {
        "filename": "olist_geolocation_dataset.csv",
        "primary_key": [],  # No strict primary key
        "date_columns": []
    },
    "order_items": {
        "filename": "olist_order_items_dataset.csv",
        "primary_key": ["order_id", "order_item_id"],
        "date_columns": ["shipping_limit_date"]
    },
    "order_payments": {
        "filename": "olist_order_payments_dataset.csv",
        "primary_key": [], # Could be order_id, payment_sequential but some might not be strictly unique
        "date_columns": []
    },
    "order_reviews": {
        "filename": "olist_order_reviews_dataset.csv",
        "primary_key": ["review_id", "order_id"],
        "date_columns": ["review_creation_date", "review_answer_timestamp"]
    },
    "orders": {
        "filename": "olist_orders_dataset.csv",
        "primary_key": ["order_id"],
        "date_columns": [
            "order_purchase_timestamp", 
            "order_approved_at", 
            "order_delivered_carrier_date", 
            "order_delivered_customer_date", 
            "order_estimated_delivery_date"
        ]
    },
    "products": {
        "filename": "olist_products_dataset.csv",
        "primary_key": ["product_id"],
        "date_columns": []
    },
    "sellers": {
        "filename": "olist_sellers_dataset.csv",
        "primary_key": ["seller_id"],
        "date_columns": []
    },
    "category_translation": {
        "filename": "product_category_name_translation.csv",
        "primary_key": ["product_category_name"],
        "date_columns": []
    }
}
