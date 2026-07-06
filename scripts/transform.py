import pandas as pd
import numpy as np
import uuid
from typing import Dict
from scripts.logger import get_logger

logger = get_logger(__name__)

def generate_surrogate_key(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df = df.copy()
    # Ensure stable ordering before assigning SK if possible, or just assign sequential
    df[col_name] = np.arange(1, len(df) + 1)
    return df

def build_dimensions(dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    logger.info("Building Dimensions...")
    dims = {}

    # Dim_Geography
    # Merge geolocation, customer city, seller city to get a unique list of geographies
    geo_df = dfs['geolocation'][['geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state']].copy()
    geo_df.columns = ['zip_code', 'city', 'state']
    
    # Also grab from ERP Warehouse and Customer Profile just to be safe
    geo_unique = geo_df.drop_duplicates(subset=['zip_code']).copy()
    geo_unique = generate_surrogate_key(geo_unique, 'geography_sk')
    dims['Dim_Geography'] = geo_unique

    # Dim_Date
    # Extract min/max dates from orders
    orders = dfs['orders']
    date_series = pd.to_datetime(orders['order_purchase_timestamp'])
    # Shift offset applies (approx 8 years) but we will just use a hardcoded wide range to cover all ERP and Order dates.
    date_range = pd.date_range(start='2022-01-01', end='2030-12-31')
    dim_date = pd.DataFrame({'full_date': date_range})
    dim_date['date_sk'] = dim_date['full_date'].dt.strftime('%Y%m%d').astype(int)
    dim_date['year'] = dim_date['full_date'].dt.year
    dim_date['month'] = dim_date['full_date'].dt.month
    dim_date['day'] = dim_date['full_date'].dt.day
    dim_date['quarter'] = dim_date['full_date'].dt.quarter
    dim_date['day_of_week'] = dim_date['full_date'].dt.dayofweek
    dim_date['is_weekend'] = dim_date['day_of_week'].isin([5, 6])
    dims['Dim_Date'] = dim_date

    # Dim_Category
    if 'category_translation' in dfs:
        cat_df = dfs['category_translation'].copy()
        cat_df.columns = ['category_name', 'category_name_english']
    else:
        cat_df = pd.DataFrame([{'category_name': 'general', 'category_name_english': 'General'}])
    cat_df = generate_surrogate_key(cat_df, 'category_sk')
    dims['Dim_Category'] = cat_df

    # Dim_Product
    pm = dfs.get('erp_product_master', pd.DataFrame())
    if not pm.empty:
        dim_prod = pm.copy()
        dim_prod = generate_surrogate_key(dim_prod, 'product_sk')
    else:
        dim_prod = pd.DataFrame(columns=['product_sk', 'product_id'])
    dims['Dim_Product'] = dim_prod

    # Dim_Customer
    cp = dfs.get('erp_customer_profile', pd.DataFrame())
    if not cp.empty:
        dim_cust = cp.copy()
        dim_cust = generate_surrogate_key(dim_cust, 'customer_sk')
    else:
        dim_cust = pd.DataFrame(columns=['customer_sk', 'customer_id'])
    dims['Dim_Customer'] = dim_cust

    # Dim_Seller
    sel = dfs['sellers'].copy()
    sel = generate_surrogate_key(sel, 'seller_sk')
    dims['Dim_Seller'] = sel[['seller_sk', 'seller_id']]

    # Dim_Warehouse
    wh = dfs.get('erp_warehouse', pd.DataFrame())
    if not wh.empty:
        dim_wh = wh.copy()
        dim_wh = generate_surrogate_key(dim_wh, 'warehouse_sk')
    else:
        dim_wh = pd.DataFrame(columns=['warehouse_sk', 'warehouse_id'])
    dims['Dim_Warehouse'] = dim_wh

    # Dim_Campaign
    mc = dfs.get('erp_marketing', pd.DataFrame())
    if not mc.empty:
        dim_camp = mc[['campaign_id', 'campaign_name', 'channel', 'campaign_type', 'start_date', 'end_date']].drop_duplicates().copy()
        dim_camp = generate_surrogate_key(dim_camp, 'campaign_sk')
    else:
        dim_camp = pd.DataFrame(columns=['campaign_sk', 'campaign_id'])
    dims['Dim_Campaign'] = dim_camp

    # Dim_Payment
    pay = dfs['order_payments'].copy()
    dim_pay = pay[['payment_type']].drop_duplicates().copy()
    dim_pay = generate_surrogate_key(dim_pay, 'payment_sk')
    dims['Dim_Payment'] = dim_pay

    # Dim_Shipping
    # We will derive this logically as carriers aren't explicitly defined in Olist (just dates and freight)
    dim_ship = pd.DataFrame({
        'carrier': ['FedEx', 'Delhivery', 'BlueDart', 'EcomExpress'],
        'shipping_method': ['Express', 'Standard', 'Standard', 'Economy']
    })
    dim_ship = generate_surrogate_key(dim_ship, 'shipping_sk')
    dims['Dim_Shipping'] = dim_ship

    return dims

def build_facts(dfs: Dict[str, pd.DataFrame], dims: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    logger.info("Building Facts...")
    facts = {}

    dim_date = dims['Dim_Date']
    dim_prod = dims['Dim_Product']
    dim_cust = dims['Dim_Customer']
    dim_sel = dims['Dim_Seller']
    dim_geo = dims['Dim_Geography']
    dim_wh = dims['Dim_Warehouse']
    dim_camp = dims['Dim_Campaign']
    dim_pay = dims['Dim_Payment']
    dim_ship = dims['Dim_Shipping']

    orders = dfs['orders'].copy()
    items = dfs['order_items'].copy()
    payments = dfs['order_payments'].copy()
    reviews = dfs['order_reviews'].copy()

    # Standardize currencies: Convert BRL to INR (exchange rate ~20)
    if 'price' in items.columns:
        items['price'] = items['price'] * 20
    if 'freight_value' in items.columns:
        items['freight_value'] = items['freight_value'] * 20
    if 'payment_value' in payments.columns:
        payments['payment_value'] = payments['payment_value'] * 20

    # Apply year shift to dates
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp']) + pd.DateOffset(years=8)
    orders['date_sk'] = orders['order_purchase_timestamp'].dt.strftime('%Y%m%d').fillna(-1).astype(int)

    # Base Join for Sales
    sales = items.merge(orders[['order_id', 'customer_id', 'order_status', 'date_sk', 
                                'order_purchase_timestamp',
                                'order_delivered_customer_date', 'order_estimated_delivery_date']], on='order_id', how='inner')
    
    # Join SKs
    sales = sales.merge(dim_cust[['customer_id', 'customer_sk']], on='customer_id', how='left')
    sales = sales.merge(dim_prod[['product_id', 'product_sk', 'cost_price']], on='product_id', how='left')
    sales = sales.merge(dim_sel[['seller_id', 'seller_sk']], on='seller_id', how='left')
    
    # Get seller_zip_code_prefix from the raw sellers dataset
    sales = sales.merge(dfs['sellers'][['seller_id', 'seller_zip_code_prefix']], on='seller_id', how='left')
    
    # Link geography to seller for now
    sales = sales.merge(dim_geo[['zip_code', 'geography_sk']], left_on='seller_zip_code_prefix', right_on='zip_code', how='left')
    
    # Dummy payment and shipping for fact sales
    sales['payment_sk'] = np.random.choice(dim_pay['payment_sk'], size=len(sales))
    sales['shipping_sk'] = np.random.choice(dim_ship['shipping_sk'], size=len(sales))
    
    sales['quantity'] = 1
    sales['discount'] = 0
    sales['unit_price'] = sales['price']
    sales['gross_sales'] = sales['unit_price'] * sales['quantity']
    sales['net_sales'] = sales['gross_sales'] - sales['discount']
    sales['profit'] = sales['net_sales'] - sales['cost_price']
    sales['margin'] = (sales['profit'] / sales['net_sales']).fillna(0)
    sales['delivery_days'] = (pd.to_datetime(sales['order_delivered_customer_date']) - pd.to_datetime(sales['order_purchase_timestamp'])).dt.days
    sales['is_delivered'] = sales['order_status'] == 'delivered'
    
    sales = generate_surrogate_key(sales, 'sales_sk')
    
    cols_sales = ['sales_sk', 'order_id', 'order_item_id', 'date_sk', 'customer_sk', 'seller_sk', 'product_sk', 'payment_sk', 'geography_sk',
                  'quantity', 'unit_price', 'discount', 'freight_value', 'cost_price', 'gross_sales', 'net_sales', 'profit', 'margin', 'delivery_days', 'is_delivered']
    
    sales.rename(columns={'freight_value_x': 'freight_value'}, inplace=True, errors='ignore')
    if 'freight_value' not in sales.columns:
        sales['freight_value'] = 0
        
    fs = sales[[c for c in cols_sales if c in sales.columns]].copy()
    fs.rename(columns={'freight_value': 'freight_cost'}, inplace=True)
    facts['Fact_Sales'] = fs

    # Fact_Inventory
    inv = dfs.get('erp_inventory', pd.DataFrame())
    if not inv.empty:
        inv['snapshot_date'] = pd.to_datetime(inv['snapshot_date'])
        inv['date_sk'] = inv['snapshot_date'].dt.strftime('%Y%m%d').fillna(-1).astype(int)
        inv = inv.merge(dim_prod[['product_id', 'product_sk']], on='product_id', how='left')
        inv = inv.merge(dim_wh[['warehouse_id', 'warehouse_sk']], on='warehouse_id', how='left')
        inv = generate_surrogate_key(inv, 'inventory_sk')
        facts['Fact_Inventory'] = inv[['inventory_sk', 'date_sk', 'warehouse_sk', 'product_sk', 'opening_stock', 'received_stock', 'sold_stock', 'damaged_stock', 'closing_stock', 'inventory_value']]

    # Fact_Marketing
    mc = dfs.get('erp_marketing', pd.DataFrame())
    if not mc.empty:
        mc['start_date'] = pd.to_datetime(mc['start_date'])
        mc['date_sk'] = mc['start_date'].dt.strftime('%Y%m%d').fillna(-1).astype(int)
        mc = mc.merge(dim_camp[['campaign_id', 'campaign_sk']], on='campaign_id', how='left')
        mc = generate_surrogate_key(mc, 'marketing_sk')
        mc.rename(columns={'daily_spend': 'spend', 'revenue_generated': 'revenue'}, inplace=True)
        facts['Fact_Marketing'] = mc[['marketing_sk', 'campaign_sk', 'date_sk', 'spend', 'impressions', 'clicks', 'ctr', 'conversions', 'revenue', 'roas', 'cpa']]

    # Fact_Returns
    returns = sales[sales['order_status'] == 'canceled'].copy()
    if not returns.empty:
        returns['reason'] = np.random.choice(['Defective', 'Changed Mind', 'Wrong Item', 'Arrived Late'], size=len(returns))
        returns['return_value'] = returns['net_sales']
        returns['refund_amount'] = returns['return_value']
        returns['days_to_return'] = np.random.randint(1, 15, size=len(returns))
        returns = generate_surrogate_key(returns, 'return_sk')
        facts['Fact_Returns'] = returns[['return_sk', 'date_sk', 'customer_sk', 'product_sk', 'reason', 'return_value', 'refund_amount', 'days_to_return']]
    else:
        facts['Fact_Returns'] = pd.DataFrame(columns=['return_sk', 'date_sk', 'customer_sk', 'product_sk', 'reason', 'return_value', 'refund_amount', 'days_to_return'])

    # Fact_Reviews
    rev = reviews.merge(orders[['order_id', 'customer_id', 'date_sk']], on='order_id', how='inner')
    rev = rev.merge(dim_cust[['customer_id', 'customer_sk']], on='customer_id', how='left')
    # Link to a random product from the order
    order_prod = items[['order_id', 'product_id']].drop_duplicates(subset=['order_id'])
    rev = rev.merge(order_prod, on='order_id', how='left')
    rev = rev.merge(dim_prod[['product_id', 'product_sk']], on='product_id', how='left')
    
    rev['sentiment_score'] = rev['review_score'] * 0.2
    rev['review_length'] = rev['review_comment_message'].str.len().fillna(0)
    rev = generate_surrogate_key(rev, 'review_sk')
    facts['Fact_Reviews'] = rev[['review_sk', 'date_sk', 'customer_sk', 'product_sk', 'review_score', 'sentiment_score', 'review_length']]

    # Fact_Payments
    pay = payments.merge(orders[['order_id', 'customer_id', 'date_sk']], on='order_id', how='inner')
    pay = pay.merge(dim_cust[['customer_id', 'customer_sk']], on='customer_id', how='left')
    pay = pay.merge(dim_pay[['payment_type', 'payment_sk']], on='payment_type', how='left')
    pay = generate_surrogate_key(pay, 'payment_sk_fact') # to avoid name clash
    pay.rename(columns={'payment_sk_fact': 'payment_sk_id', 'payment_installments': 'installments', 'payment_type': 'payment_method'}, inplace=True)
    facts['Fact_Payments'] = pay[['payment_sk_id', 'date_sk', 'customer_sk', 'payment_method', 'installments', 'payment_value']].rename(columns={'payment_sk_id': 'payment_sk'})

    # Fact_Shipping
    ship = sales[['date_sk', 'seller_sk', 'customer_sk', 'shipping_sk', 'freight_value', 'delivery_days']].copy()
    ship = ship.merge(dim_ship, on='shipping_sk', how='left')
    ship['shipping_cost'] = ship['freight_value']
    ship['estimated_days'] = ship['delivery_days'] + np.random.randint(-2, 5, size=len(ship))
    ship['actual_days'] = ship['delivery_days']
    ship['late_delivery'] = ship['actual_days'] > ship['estimated_days']
    ship = generate_surrogate_key(ship, 'shipping_sk_fact')
    facts['Fact_Shipping'] = ship[['shipping_sk_fact', 'date_sk', 'seller_sk', 'customer_sk', 'carrier', 'shipping_method', 'shipping_cost', 'estimated_days', 'actual_days', 'late_delivery']].rename(columns={'shipping_sk_fact': 'shipping_sk'})

    return facts

def transform_data(dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Orchestrate cleaning AND dimensional modeling for all loaded datasets.
    """
    logger.info("Transform Phase: Generating Star Schema...")
    
    # 1. Generate Dimensions
    dims = build_dimensions(dfs)
    
    # 2. Generate Facts
    facts = build_facts(dfs, dims)
    
    # 3. Combine output
    star_schema = {**dims, **facts}
    
    return star_schema
