import pandas as pd
import numpy as np
from pathlib import Path
import sys
import uuid
import random

sys.path.append(str(Path(__file__).parent.parent))
from scripts.config import DATA_PROCESSED_DIR, DATA_ERP_CRM_DIR
from scripts.logger import get_logger

logger = get_logger(__name__)

# Constants
COLLECTIONS = ["Scandinavian", "Minimalist", "Luxury", "Festive", "Bohemian", "Vintage", "Modern"]
MATERIALS = ["Ceramic", "Glass", "Wood", "Metal", "Marble", "Bamboo", "Cotton", "Linen"]
COLORS = ["White", "Black", "Gold", "Silver", "Beige", "Navy", "Emerald", "Rust"]
SIZES = ["Small", "Medium", "Large", "Standard"]
SUPPLIERS = ["Nestasia Mfg", "Global Decor Co", "Artisan Crafts India", "Prime Home Goods"]

WAREHOUSE_DATA = [
    {"warehouse_id": "WH_MUM_01", "warehouse_name": "Mumbai Central Hub", "city": "Mumbai", "state": "Maharashtra", "country": "India", "capacity": 50000, "manager": "Ravi Patel", "warehouse_type": "Fulfillment", "latitude": 19.0760, "longitude": 72.8777},
    {"warehouse_id": "WH_DEL_02", "warehouse_name": "Delhi NCR Depot", "city": "Delhi", "state": "Delhi", "country": "India", "capacity": 60000, "manager": "Sunita Sharma", "warehouse_type": "Fulfillment", "latitude": 28.7041, "longitude": 77.1025},
    {"warehouse_id": "WH_BLR_03", "warehouse_name": "Bangalore South WH", "city": "Bangalore", "state": "Karnataka", "country": "India", "capacity": 45000, "manager": "Vikram Singh", "warehouse_type": "Fulfillment", "latitude": 12.9716, "longitude": 77.5946},
    {"warehouse_id": "WH_KOL_04", "warehouse_name": "Kolkata East Terminal", "city": "Kolkata", "state": "West Bengal", "country": "India", "capacity": 30000, "manager": "Amit Bose", "warehouse_type": "Distribution", "latitude": 22.5726, "longitude": 88.3639}
]

CAMPAIGN_TYPES = ["Awareness", "Conversion", "Retargeting", "Holiday"]
CHANNELS = ["Google Search", "Facebook", "Instagram", "Email", "YouTube"]
CAMPAIGN_NAMES = ["Diwali Bonanza", "Summer Refresh", "Festive Highlights", "Minimalist Living", "Clearance Sale"]

YEAR_OFFSET = 8  # Shifts Olist dates to 2024-2026

def generate_warehouse():
    logger.info("Generating Warehouse.csv...")
    wh_df = pd.DataFrame(WAREHOUSE_DATA)
    wh_df.to_csv(DATA_ERP_CRM_DIR / "Warehouse.csv", index=False)
    logger.info(f"Generated Warehouse.csv with {len(wh_df)} rows.")
    return wh_df

def generate_product_master(products_df, order_items_df):
    logger.info("Generating Product_Master.csv...")
    np.random.seed(42)
    
    price_df = order_items_df.groupby('product_id')['price'].median().reset_index()
    pm = products_df[['product_id']].copy()
    pm = pm.merge(price_df, on='product_id', how='left')
    pm['price'] = pm['price'].fillna(np.random.uniform(400, 4000))
    
    n = len(pm)
    pm['sku'] = [f"NST-{str(uuid.uuid4())[:8].upper()}" for _ in range(n)]
    pm['brand'] = 'Nestasia'
    pm['collection'] = np.random.choice(COLLECTIONS, size=n)
    pm['material'] = np.random.choice(MATERIALS, size=n)
    pm['color'] = np.random.choice(COLORS, size=n)
    pm['size'] = np.random.choice(SIZES, size=n)
    pm['supplier'] = np.random.choice(SUPPLIERS, size=n)
    
    pm['mrp'] = (pm['price'] * np.random.uniform(1.2, 1.5, size=n)).round(0)
    pm['cost_price'] = (pm['price'] * np.random.uniform(0.3, 0.6, size=n)).round(2)
    
    pm['launch_date'] = pd.to_datetime('2023-01-01') + pd.to_timedelta(np.random.randint(0, 365, size=n), unit='d')
    pm['product_status'] = np.random.choice(['Active', 'Discontinued', 'Out of Stock'], p=[0.85, 0.1, 0.05], size=n)
    
    cols = ['product_id', 'sku', 'brand', 'collection', 'material', 'color', 'size', 'supplier', 'cost_price', 'mrp', 'launch_date', 'product_status']
    pm = pm[cols]
    pm.to_csv(DATA_ERP_CRM_DIR / "Product_Master.csv", index=False)
    logger.info(f"Generated Product_Master.csv with {len(pm)} rows.")
    return pm

def generate_inventory(products_df, order_items_df, warehouse_df):
    logger.info("Generating Inventory.csv...")
    np.random.seed(43)
    
    sold_qty = order_items_df.groupby('product_id').size().reset_index(name='sold_stock')
    inv = products_df[['product_id']].copy()
    inv = inv.merge(sold_qty, on='product_id', how='left')
    inv['sold_stock'] = inv['sold_stock'].fillna(0).astype(int)
    
    n = len(inv)
    inv['inventory_id'] = [f"INV_{i+1000}" for i in range(n)]
    inv['warehouse_id'] = np.random.choice(warehouse_df['warehouse_id'], size=n)
    inv['snapshot_date'] = pd.to_datetime('today').date()
    
    inv['closing_stock'] = np.random.randint(10, 500, size=n)
    inv['damaged_stock'] = np.random.randint(0, 10, size=n)
    inv['received_stock'] = inv['sold_stock'] + np.random.randint(10, 200, size=n)
    inv['opening_stock'] = (inv['closing_stock'] + inv['sold_stock'] + inv['damaged_stock'] - inv['received_stock']).clip(lower=0)
    inv['received_stock'] = inv['closing_stock'] + inv['sold_stock'] + inv['damaged_stock'] - inv['opening_stock']
    
    inv['reorder_level'] = np.random.randint(20, 100, size=n)
    
    pm = pd.read_csv(DATA_ERP_CRM_DIR / "Product_Master.csv")
    inv = inv.merge(pm[['product_id', 'cost_price']], on='product_id', how='left')
    inv['inventory_value'] = (inv['closing_stock'] * inv['cost_price']).round(2)
    
    inv['stock_status'] = np.where(inv['closing_stock'] == 0, 'Out of Stock',
                          np.where(inv['closing_stock'] <= inv['reorder_level'], 'Reorder', 'Healthy'))
    
    cols = ['inventory_id', 'product_id', 'warehouse_id', 'snapshot_date', 'opening_stock', 'received_stock', 'sold_stock', 'damaged_stock', 'closing_stock', 'reorder_level', 'inventory_value', 'stock_status']
    inv = inv[cols]
    inv.to_csv(DATA_ERP_CRM_DIR / "Inventory.csv", index=False)
    logger.info(f"Generated Inventory.csv with {len(inv)} rows.")

def generate_customer_profile(customers_df, orders_df):
    logger.info("Generating Customer_Profile.csv...")
    np.random.seed(44)
    
    cp = customers_df[['customer_id', 'customer_city', 'customer_state']].copy()
    cp.rename(columns={'customer_city': 'city', 'customer_state': 'state'}, inplace=True)
    
    n = len(cp)
    cp['gender'] = np.random.choice(['Male', 'Female', 'Other'], p=[0.45, 0.53, 0.02], size=n)
    cp['age'] = np.random.normal(loc=35, scale=12, size=n).clip(18, 75).astype(int)
    
    bins = [17, 25, 35, 45, 55, 100]
    labels = ['18-25', '26-35', '36-45', '46-55', '55+']
    cp['age_group'] = pd.cut(cp['age'], bins=bins, labels=labels)
    
    cp['income_segment'] = np.random.choice(['Low', 'Medium', 'High', 'Premium'], p=[0.2, 0.5, 0.2, 0.1], size=n)
    cp['country'] = 'India'
    cp['loyalty_tier'] = np.random.choice(['Silver', 'Gold', 'Platinum'], p=[0.7, 0.2, 0.1], size=n)
    
    # Signup date
    first_orders = orders_df.groupby('customer_id')['order_purchase_timestamp'].min().reset_index()
    first_orders['order_purchase_timestamp'] = pd.to_datetime(first_orders['order_purchase_timestamp']) + pd.DateOffset(years=YEAR_OFFSET)
    cp = cp.merge(first_orders, on='customer_id', how='left')
    cp['signup_date'] = (cp['order_purchase_timestamp'] - pd.to_timedelta(np.random.randint(0, 30, size=n), unit='d')).dt.date
    
    cp['preferred_channel'] = np.random.choice(['Web', 'App', 'In-Store'], p=[0.4, 0.5, 0.1], size=n)
    cp['customer_segment'] = np.random.choice(['Bargain Hunter', 'Brand Loyalist', 'Impulse Buyer', 'Occasional Buyer'], p=[0.3, 0.2, 0.2, 0.3], size=n)
    cp['estimated_clv'] = np.random.uniform(5000, 50000, size=n).round(2)
    
    cols = ['customer_id', 'gender', 'age', 'age_group', 'income_segment', 'city', 'state', 'country', 'loyalty_tier', 'signup_date', 'preferred_channel', 'customer_segment', 'estimated_clv']
    cp = cp[cols]
    cp.to_csv(DATA_ERP_CRM_DIR / "Customer_Profile.csv", index=False)
    logger.info(f"Generated Customer_Profile.csv with {len(cp)} rows.")

def generate_marketing_campaign():
    logger.info("Generating Marketing_Campaign.csv...")
    np.random.seed(45)
    
    records = []
    start_date = pd.to_datetime('2024-01-01')
    
    for i in range(1, 201):  # Generate 200 campaigns
        channel = np.random.choice(CHANNELS)
        ctype = np.random.choice(CAMPAIGN_TYPES)
        name = np.random.choice(CAMPAIGN_NAMES)
        
        c_start = start_date + pd.Timedelta(days=np.random.randint(0, 700))
        c_end = c_start + pd.Timedelta(days=np.random.randint(7, 90))
        
        daily_spend = np.random.uniform(1000, 10000)
        days = (c_end - c_start).days
        total_spend = daily_spend * days
        
        cpc = np.random.uniform(10, 50)
        clicks = int(total_spend / cpc)
        ctr = np.random.uniform(0.005, 0.05)
        impressions = int(clicks / ctr)
        
        conv_rate = np.random.uniform(0.01, 0.05)
        conversions = int(clicks * conv_rate)
        
        aov = np.random.uniform(1000, 3000)
        revenue = conversions * aov
        
        roas = revenue / total_spend if total_spend > 0 else 0
        cpa = total_spend / conversions if conversions > 0 else total_spend
        
        records.append({
            'campaign_id': f"CMP_{i:04d}",
            'campaign_name': f"{name} {c_start.strftime('%b %Y')}",
            'channel': channel,
            'campaign_type': ctype,
            'start_date': c_start.date(),
            'end_date': c_end.date(),
            'daily_spend': round(daily_spend, 2),
            'impressions': impressions,
            'clicks': clicks,
            'ctr': round(ctr * 100, 2),
            'conversions': conversions,
            'conversion_rate': round(conv_rate * 100, 2),
            'revenue_generated': round(revenue, 2),
            'roas': round(roas, 2),
            'cpa': round(cpa, 2)
        })
        
    mc = pd.DataFrame(records)
    mc.to_csv(DATA_ERP_CRM_DIR / "Marketing_Campaign.csv", index=False)
    logger.info(f"Generated Marketing_Campaign.csv with {len(mc)} rows.")

if __name__ == "__main__":
    logger.info("--- Starting ERP/CRM Dataset Generation ---")
    
    try:
        products_df = pd.read_csv(DATA_PROCESSED_DIR / "products_cleaned.csv")
        customers_df = pd.read_csv(DATA_PROCESSED_DIR / "customers_cleaned.csv")
        order_items_df = pd.read_csv(DATA_PROCESSED_DIR / "order_items_cleaned.csv")
        orders_df = pd.read_csv(DATA_PROCESSED_DIR / "orders_cleaned.csv")
        
        warehouse_df = generate_warehouse()
        generate_product_master(products_df, order_items_df)
        generate_inventory(products_df, order_items_df, warehouse_df)
        generate_customer_profile(customers_df, orders_df)
        generate_marketing_campaign()
        
        # Remove Calendar.csv if it existed, we aren't asked to generate it now. (Actually I'll just leave it or overwrite)
        
        logger.info("--- ERP/CRM Dataset Generation Completed Successfully ---")
        
    except FileNotFoundError as e:
        logger.error(f"Missing required Olist cleaned dataset: {e}")
