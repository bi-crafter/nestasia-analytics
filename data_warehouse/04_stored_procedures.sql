-- Enterprise Retail Analytics - Procedures (MySQL)

USE nestasia_dwh;

-- =========================================
-- STORED PROCEDURES
-- =========================================

DELIMITER //

-- Procedure for slowly changing dimension (SCD Type 1) update for Product
CREATE PROCEDURE sp_upsert_dim_product(
    IN p_product_id VARCHAR(50),
    IN p_sku VARCHAR(50),
    IN p_brand VARCHAR(50),
    IN p_collection VARCHAR(100),
    IN p_cost_price DECIMAL(10,2),
    IN p_mrp DECIMAL(10,2),
    IN p_product_status VARCHAR(50)
)
BEGIN
    DECLARE v_product_sk INT;
    
    SELECT product_sk INTO v_product_sk 
    FROM Dim_Product 
    WHERE product_id = p_product_id;
    
    IF v_product_sk IS NOT NULL THEN
        -- Update existing record (Type 1)
        UPDATE Dim_Product
        SET sku = p_sku,
            brand = p_brand,
            collection = p_collection,
            cost_price = p_cost_price,
            mrp = p_mrp,
            product_status = p_product_status
        WHERE product_sk = v_product_sk;
    ELSE
        -- Insert new record
        -- Assuming surrogate key auto increments in real engine, though we modeled as INT PRIMARY KEY
        INSERT INTO Dim_Product (product_id, sku, brand, collection, cost_price, mrp, product_status)
        VALUES (p_product_id, p_sku, p_brand, p_collection, p_cost_price, p_mrp, p_product_status);
    END IF;
END //

DELIMITER ;
