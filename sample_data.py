import random
from decimal import Decimal
from database import execute_query

def insert_sample_data():
    """
    Inserts demo data into MySQL tables: products, customers, and sales.
    """
    print("[sample_data] Inserting demo data...")

    # Sample products
    products = [
        {"name": "Laptop", "category": "Electronics", "price": 899.99},
        {"name": "Mouse", "category": "Electronics", "price": 24.99},
        {"name": "Keyboard", "category": "Electronics", "price": 49.99},
        {"name": "Chair", "category": "Furniture", "price": 119.99},
        {"name": "Desk", "category": "Furniture", "price": 249.99},
        {"name": "Notebook", "category": "Stationery", "price": 4.99},
        {"name": "Pen", "category": "Stationery", "price": 1.99},
    ]

    for p in products:
        execute_query(
            "INSERT IGNORE INTO products (name, category, price) VALUES (%s,%s,%s)",
            (p["name"], p["category"], p["price"]),
            commit=True,
        )

    # Sample customers
    customers = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "2345678901"},
        {"name": "Charlie Davis", "email": "charlie@example.com", "phone": "3456789012"},
        {"name": "Diana Prince", "email": "diana@example.com", "phone": "4567890123"},
    ]

    for c in customers:
        execute_query(
            "INSERT IGNORE INTO customers (name, email, phone) VALUES (%s,%s,%s)",
            (c["name"], c["email"], c["phone"]),
            commit=True,
        )

    # Sample sales
    products = execute_query("SELECT id, price FROM products")
    customers = execute_query("SELECT id FROM customers")

    for _ in range(20):
        prod = random.choice(products)
        cust = random.choice(customers)
        price = Decimal(str(prod["price"]))  # Ensure it's Decimal-safe
        amt = round(float(price) * random.uniform(0.9, 1.1), 2)

        execute_query(
            "INSERT INTO sales (product_id, customer_id, sale_date, amount) VALUES (%s,%s,NOW(),%s)",
            (prod["id"], cust["id"], amt),
            commit=True,
        )

    print("[sample_data] Demo data inserted successfully!")
