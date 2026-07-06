import getpass, sys
from sqlalchemy import create_engine, text
from pathlib import Path

def reset_schema():
    print('Enter MySQL Connection Details:')
    user = input('Username (default root): ') or 'root'
    password = getpass.getpass('Password: ')
    host = input('Host (default localhost): ') or 'localhost'
    port = input('Port (default 3306): ') or '3306'
    
    try:
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/')
        with engine.begin() as conn:
            conn.execute(text('DROP DATABASE IF EXISTS nestasia_dwh'))
            conn.execute(text('CREATE DATABASE nestasia_dwh'))
            print('Database reset successfully.')
            
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/nestasia_dwh')
        
        # Read and execute schema
        schema_path = Path('data_warehouse/01_schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_statements = f.read().split(';')
            
        with engine.begin() as conn:
            for stmt in sql_statements:
                if stmt.strip():
                    conn.execute(text(stmt))
        print('Schema created successfully.')
        
        # Read and execute indexes
        indexes_path = Path('data_warehouse/02_indexes.sql')
        with open(indexes_path, 'r', encoding='utf-8') as f:
            sql_statements = f.read().split(';')
            
        with engine.begin() as conn:
            for stmt in sql_statements:
                if stmt.strip():
                    conn.execute(text(stmt))
        print('Indexes and Foreign Keys created successfully.')
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    reset_schema()
