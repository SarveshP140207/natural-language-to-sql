import os
import random
from datetime import datetime, timedelta

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE", "ecommerce_db"),
}


CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home Appliances",
    "Books",
    "Sports",
    "Beauty",
    "Groceries",
    "Furniture",
    "Toys",
    "Automotive",
    "Footwear",
    "Jewelry",
    "Stationery",
    "Kitchen",
    "Gaming"
]


FIRST_NAMES = [
    "Arun", "Karthik", "Rahul", "Vijay", "Surya",
    "Ajay", "Rohan", "Sanjay", "Aditya", "Naveen",
    "Priya", "Ananya", "Divya", "Sneha", "Meera",
    "Keerthi", "Pooja", "Kavya", "Aishwarya", "Nisha"
]


LAST_NAMES = [
    "Kumar", "Raj", "Sharma", "Patel", "Singh",
    "Reddy", "Iyer", "Nair", "Menon", "Das",
    "Verma", "Gupta", "Rao", "Joshi", "Mishra"
]


CITY_STATE_PAIRS = [
    ("Chennai", "Tamil Nadu"),
    ("Coimbatore", "Tamil Nadu"),
    ("Madurai", "Tamil Nadu"),
    ("Bangalore", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Mumbai", "Maharashtra"),
    ("Pune", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Kochi", "Kerala"),
    ("Kolkata", "West Bengal")
]


PRODUCT_NAMES = {
    "Electronics": [
        "Wireless Headphones",
        "Smartphone",
        "Bluetooth Speaker",
        "Laptop",
        "Smart Watch"
    ],
    "Clothing": [
        "T-Shirt",
        "Jeans",
        "Hoodie",
        "Formal Shirt",
        "Jacket"
    ],
    "Home Appliances": [
        "Mixer Grinder",
        "Microwave Oven",
        "Air Conditioner",
        "Electric Kettle",
        "Washing Machine"
    ],
    "Books": [
        "Python Programming",
        "Data Structures",
        "Machine Learning",
        "Database Systems",
        "Computer Networks"
    ],
    "Sports": [
        "Cricket Bat",
        "Football",
        "Tennis Racket",
        "Yoga Mat",
        "Running Shoes"
    ],
    "Beauty": [
        "Face Wash",
        "Moisturizer",
        "Shampoo",
        "Perfume",
        "Sunscreen"
    ],
    "Groceries": [
        "Rice Pack",
        "Wheat Flour",
        "Cooking Oil",
        "Coffee Powder",
        "Breakfast Cereal"
    ],
    "Furniture": [
        "Office Chair",
        "Study Table",
        "Bookshelf",
        "Sofa",
        "Dining Table"
    ],
    "Toys": [
        "Remote Car",
        "Building Blocks",
        "Board Game",
        "Toy Robot",
        "Puzzle Set"
    ],
    "Automotive": [
        "Car Cover",
        "Bike Helmet",
        "Engine Oil",
        "Car Vacuum",
        "Dash Camera"
    ],
    "Footwear": [
        "Running Shoes",
        "Casual Shoes",
        "Sports Sandals",
        "Formal Shoes",
        "Slippers"
    ],
    "Jewelry": [
        "Necklace",
        "Bracelet",
        "Ring",
        "Earrings",
        "Pendant"
    ],
    "Stationery": [
        "Notebook",
        "Ball Pen Set",
        "Marker Set",
        "Drawing Book",
        "File Folder"
    ],
    "Kitchen": [
        "Non Stick Pan",
        "Pressure Cooker",
        "Knife Set",
        "Dinner Set",
        "Storage Container"
    ],
    "Gaming": [
        "Gaming Mouse",
        "Mechanical Keyboard",
        "Game Controller",
        "Gaming Headset",
        "Mouse Pad"
    ]
}


PAYMENT_METHODS = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Cash on Delivery"
]


ORDER_STATUSES = [
    "Delivered",
    "Delivered",
    "Delivered",
    "Delivered",
    "Shipped",
    "Processing",
    "Cancelled"
]


REVIEW_TEXTS = [
    "Very good product",
    "Worth the money",
    "Excellent quality",
    "Good product",
    "Satisfied with the purchase",
    "Average product",
    "Could be better",
    "Amazing experience"
]


def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def clear_existing_data(cursor):
    print("Clearing existing generated data...")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    tables = [
        "reviews",
        "payments",
        "order_items",
        "orders",
        "products",
        "customers",
        "categories"
    ]

    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table}")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def main():
    print("Connecting to MySQL...")

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    print("Connected successfully.")

    clear_existing_data(cursor)

    print("Creating categories...")

    category_ids = {}

    for category_name in CATEGORIES:
        cursor.execute(
            """
            INSERT INTO categories (category_name)
            VALUES (%s)
            """,
            (category_name,)
        )

        category_ids[category_name] = cursor.lastrowid

    print("Creating customers...")

    customer_ids = []

    for i in range(100):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        email = f"{first_name.lower()}.{last_name.lower()}.{i + 1}@example.com"

        phone = f"9{random.randint(100000000, 999999999)}"

        city, state = random.choice(CITY_STATE_PAIRS)

        registration_date = random_date(
            datetime(2024, 1, 1),
            datetime(2025, 12, 31)
        ).date()

        cursor.execute(
            """
            INSERT INTO customers
            (first_name, last_name, email, phone, city, state, registration_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                first_name,
                last_name,
                email,
                phone,
                city,
                state,
                registration_date
            )
        )

        customer_ids.append(cursor.lastrowid)

    print("Creating products...")

    product_ids = []

    for category_name, names in PRODUCT_NAMES.items():
        category_id = category_ids[category_name]

        for product_name in names:
            price = round(random.uniform(500, 150000), 2)

            stock_quantity = random.randint(0, 500)

            created_date = random_date(
                datetime(2024, 1, 1),
                datetime(2025, 12, 31)
            ).date()

            cursor.execute(
                """
                INSERT INTO products
                (product_name, category_id, price, stock_quantity, created_date)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    product_name,
                    category_id,
                    price,
                    stock_quantity,
                    created_date
                )
            )

            product_ids.append(
                (
                    cursor.lastrowid,
                    price
                )
            )

    print("Creating orders and order items...")

    order_ids = []

    for _ in range(500):
        customer_id = random.choice(customer_ids)

        order_date = random_date(
            datetime(2025, 1, 1),
            datetime(2026, 9, 30)
        )

        status = random.choice(ORDER_STATUSES)

        selected_products = random.sample(
            product_ids,
            random.randint(1, 4)
        )

        order_items_data = []
        total_amount = 0

        for product_id, product_price in selected_products:
            quantity = random.randint(1, 5)

            order_items_data.append(
                (
                    product_id,
                    quantity,
                    product_price
                )
            )

            total_amount += quantity * product_price

        total_amount = round(total_amount, 2)

        cursor.execute(
            """
            INSERT INTO orders
            (customer_id, order_date, status, total_amount)
            VALUES (%s, %s, %s, %s)
            """,
            (
                customer_id,
                order_date,
                status,
                total_amount
            )
        )

        order_id = cursor.lastrowid
        order_ids.append(order_id)

        for product_id, quantity, unit_price in order_items_data:
            cursor.execute(
                """
                INSERT INTO order_items
                (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price
                )
            )

    print("Creating payments...")

    for order_id in order_ids:
        cursor.execute(
            """
            SELECT order_date, total_amount, status
            FROM orders
            WHERE order_id = %s
            """,
            (order_id,)
        )

        order_date, total_amount, status = cursor.fetchone()

        payment_date = order_date + timedelta(
            days=random.randint(0, 3)
        )

        payment_method = random.choice(PAYMENT_METHODS)

        if status == "Cancelled":
            payment_status = "Failed"
            amount = 0
        else:
            payment_status = "Completed"
            amount = total_amount

        cursor.execute(
            """
            INSERT INTO payments
            (order_id, payment_date, amount, payment_method, payment_status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                order_id,
                payment_date,
                amount,
                payment_method,
                payment_status
            )
        )

    print("Creating reviews...")

    for _ in range(300):
        product_id, _ = random.choice(product_ids)
        customer_id = random.choice(customer_ids)

        rating = random.randint(1, 5)

        review_text = random.choice(REVIEW_TEXTS)

        review_date = random_date(
            datetime(2025, 1, 1),
            datetime(2026, 9, 30)
        ).date()

        cursor.execute(
            """
            INSERT INTO reviews
            (product_id, customer_id, rating, review_text, review_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                product_id,
                customer_id,
                rating,
                review_text,
                review_date
            )
        )

    connection.commit()

    print()
    print("Data generation completed successfully.")
    print()

    tables = [
        "categories",
        "customers",
        "products",
        "orders",
        "order_items",
        "payments",
        "reviews"
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} rows")

    cursor.close()
    connection.close()

    print()
    print("MySQL connection closed.")


if __name__ == "__main__":
    main()