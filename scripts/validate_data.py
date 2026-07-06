import getpass
import pandas as pd
from sqlalchemy import create_engine, text

def validate_data():
    print("Enter MySQL Connection Details to Validate Data:")
    user = input("Username (default root): ") or 'root'
    password = getpass.getpass("Password: ")
    host = input("Host (default localhost): ") or 'localhost'
    port = input("Port (default 3306): ") or '3306'
    database = 'nestasia_dwh'
    
    try:
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
        
        # Check 1: Row Counts for all Tables
        print("\n--- 1. TABLE ROW COUNTS ---")
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'nestasia_dwh' 
            AND table_name NOT LIKE 'mv_%'
            ORDER BY table_name;
        """)
        
        with engine.connect() as conn:
            tables = [row[0] for row in conn.execute(tables_query)]
            for table in tables:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"{table:<20} : {count:,} rows")
                
        # Check 2: Total Sales vs Total Marketing Spend
        print("\n--- 2. KEY METRICS VALIDATION ---")
        with engine.connect() as conn:
            total_sales = conn.execute(text("SELECT SUM(net_sales) FROM Fact_Sales")).scalar() or 0
            total_marketing = conn.execute(text("SELECT SUM(spend) FROM Fact_Marketing")).scalar() or 0
            total_customers = conn.execute(text("SELECT COUNT(DISTINCT customer_sk) FROM Fact_Sales")).scalar() or 0
            
            print(f"Total Net Sales      : ₹ {total_sales:,.2f}")
            print(f"Total Marketing Spend: ₹ {total_marketing:,.2f}")
            print(f"Unique Customers     : {total_customers:,}")

        # Check 3: Missing or NULL Foreign Keys
        print("\n--- 3. DATA INTEGRITY (NULL CHECKS) ---")
        with engine.connect() as conn:
            null_customers = conn.execute(text("SELECT COUNT(*) FROM Fact_Sales WHERE customer_sk IS NULL")).scalar()
            null_products = conn.execute(text("SELECT COUNT(*) FROM Fact_Sales WHERE product_sk IS NULL")).scalar()
            null_dates = conn.execute(text("SELECT COUNT(*) FROM Fact_Sales WHERE date_sk IS NULL")).scalar()
            
            print(f"Orphaned Customers in Sales: {null_customers}")
            print(f"Orphaned Products in Sales : {null_products}")
            print(f"Missing Dates in Sales     : {null_dates}")
            
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == '__main__':
    validate_data()
