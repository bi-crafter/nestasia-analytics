-- Enterprise Retail Analytics - Indexes & Constraints (MySQL)

USE nestasia_dwh;

-- =========================================
-- FOREIGN KEY CONSTRAINTS
-- =========================================

-- FACT_SALES
ALTER TABLE Fact_Sales
ADD CONSTRAINT fk_sales_date FOREIGN KEY (date_sk) REFERENCES Dim_Date(date_sk),
ADD CONSTRAINT fk_sales_customer FOREIGN KEY (customer_sk) REFERENCES Dim_Customer(customer_sk),
ADD CONSTRAINT fk_sales_product FOREIGN KEY (product_sk) REFERENCES Dim_Product(product_sk),
ADD CONSTRAINT fk_sales_seller FOREIGN KEY (seller_sk) REFERENCES Dim_Seller(seller_sk),
ADD CONSTRAINT fk_sales_geography FOREIGN KEY (geography_sk) REFERENCES Dim_Geography(geography_sk),
ADD CONSTRAINT fk_sales_payment FOREIGN KEY (payment_sk) REFERENCES Dim_Payment(payment_sk);

-- FACT_INVENTORY
ALTER TABLE Fact_Inventory
ADD CONSTRAINT fk_inv_date FOREIGN KEY (date_sk) REFERENCES Dim_Date(date_sk),
ADD CONSTRAINT fk_inv_warehouse FOREIGN KEY (warehouse_sk) REFERENCES Dim_Warehouse(warehouse_sk),
ADD CONSTRAINT fk_inv_product FOREIGN KEY (product_sk) REFERENCES Dim_Product(product_sk);

-- FACT_MARKETING
ALTER TABLE Fact_Marketing
ADD CONSTRAINT fk_mkt_date FOREIGN KEY (date_sk) REFERENCES Dim_Date(date_sk),
ADD CONSTRAINT fk_mkt_campaign FOREIGN KEY (campaign_sk) REFERENCES Dim_Campaign(campaign_sk);

-- FACT_RETURNS
ALTER TABLE Fact_Returns
ADD CONSTRAINT fk_ret_date FOREIGN KEY (date_sk) REFERENCES Dim_Date(date_sk),
ADD CONSTRAINT fk_ret_customer FOREIGN KEY (customer_sk) REFERENCES Dim_Customer(customer_sk),
ADD CONSTRAINT fk_ret_product FOREIGN KEY (product_sk) REFERENCES Dim_Product(product_sk);

-- FACT_REVIEWS
ALTER TABLE Fact_Reviews
ADD CONSTRAINT fk_rev_date FOREIGN KEY (date_sk) REFERENCES Dim_Date(date_sk),
ADD CONSTRAINT fk_rev_customer FOREIGN KEY (customer_sk) REFERENCES Dim_Customer(customer_sk),
ADD CONSTRAINT fk_rev_product FOREIGN KEY (product_sk) REFERENCES Dim_Product(product_sk);

-- FACT_PAYMENTS
ALTER TABLE Fact_Payments
ADD CONSTRAINT fk_pay_date FOREIGN KEY (date_sk) REFERENCES Dim_Date(date_sk),
ADD CONSTRAINT fk_pay_customer FOREIGN KEY (customer_sk) REFERENCES Dim_Customer(customer_sk);

-- FACT_SHIPPING
ALTER TABLE Fact_Shipping
ADD CONSTRAINT fk_ship_date FOREIGN KEY (date_sk) REFERENCES Dim_Date(date_sk),
ADD CONSTRAINT fk_ship_seller FOREIGN KEY (seller_sk) REFERENCES Dim_Seller(seller_sk),
ADD CONSTRAINT fk_ship_customer FOREIGN KEY (customer_sk) REFERENCES Dim_Customer(customer_sk);

-- =========================================
-- B-TREE PERFORMANCE INDEXES
-- =========================================

-- Dim_Product
CREATE INDEX idx_dim_product_sku ON Dim_Product(sku);
CREATE INDEX idx_dim_product_category ON Dim_Product(collection);

-- Fact_Sales
CREATE INDEX idx_fact_sales_date ON Fact_Sales(date_sk);
CREATE INDEX idx_fact_sales_product ON Fact_Sales(product_sk);
CREATE INDEX idx_fact_sales_customer ON Fact_Sales(customer_sk);

-- Fact_Inventory
CREATE INDEX idx_fact_inv_warehouse_prod ON Fact_Inventory(warehouse_sk, product_sk, date_sk);

-- Fact_Marketing
CREATE INDEX idx_fact_mkt_campaign_date ON Fact_Marketing(campaign_sk, date_sk);
