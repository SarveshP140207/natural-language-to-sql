import os
import random
from datetime import datetime, timedelta

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_WRITER_USER"),
    "password": os.getenv("MYSQL_WRITER_PASSWORD"),
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
    "Gaming",
]


FIRST_NAMES = [
    "Arun", "Karthik", "Rahul", "Vijay", "Surya",
    "Ajay", "Rohan", "Sanjay", "Aditya", "Naveen",
    "Priya", "Ananya", "Divya", "Sneha", "Meera",
    "Keerthi", "Pooja", "Kavya", "Aishwarya", "Nisha",
]


LAST_NAMES = [
    "Kumar", "Raj", "Sharma", "Patel", "Singh",
    "Reddy", "Iyer", "Nair", "Menon", "Das",
    "Verma", "Gupta", "Rao", "Joshi", "Mishra",
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
    ("Kolkata", "West Bengal"),
]


# Product name -> (category, minimum price, maximum price,
#                  minimum stock, maximum stock)
PRODUCTS = [
    ("Wireless Headphones", "Electronics", 1200, 8000, 10, 120),
    ("Smartphone", "Electronics", 10000, 75000, 5, 80),
    ("Bluetooth Speaker", "Electronics", 900, 7000, 10, 100),
    ("Laptop", "Electronics", 35000, 120000, 3, 40),
    ("Smart Watch", "Electronics", 1800, 18000, 5, 70),

    ("T-Shirt", "Clothing", 300, 1800, 20, 200),
    ("Jeans", "Clothing", 900, 4500, 15, 150),
    ("Hoodie", "Clothing", 1000, 3500, 10, 120),
    ("Formal Shirt", "Clothing", 700, 3000, 15, 140),
    ("Jacket", "Clothing", 1500, 7000, 8, 80),

    ("Mixer Grinder", "Home Appliances", 2200, 9000, 5, 70),
    ("Microwave Oven", "Home Appliances", 6000, 18000, 3, 40),
    ("Air Conditioner", "Home Appliances", 28000, 65000, 2, 25),
    ("Electric Kettle", "Home Appliances", 900, 3500, 10, 100),
    ("Washing Machine", "Home Appliances", 18000, 50000, 2, 30),

    ("Python Programming", "Books", 400, 1800, 10, 100),
    ("Data Structures", "Books", 450, 2000, 10, 100),
    ("Machine Learning", "Books", 500, 2500, 8, 80),
    ("Database Systems", "Books", 450, 2200, 8, 80),
    ("Computer Networks", "Books", 400, 2000, 8, 80),

    ("Cricket Bat", "Sports", 1200, 12000, 5, 60),
    ("Football", "Sports", 500, 3000, 10, 100),
    ("Tennis Racket", "Sports", 1500, 10000, 5, 50),
    ("Yoga Mat", "Sports", 400, 2500, 10, 100),
    ("Training Shoes", "Sports", 1200, 6000, 10, 100),

    ("Face Wash", "Beauty", 150, 900, 20, 200),
    ("Moisturizer", "Beauty", 250, 1800, 15, 150),
    ("Shampoo", "Beauty", 200, 1200, 20, 200),
    ("Perfume", "Beauty", 600, 7000, 10, 100),
    ("Sunscreen", "Beauty", 300, 1600, 15, 150),

    ("Rice Pack", "Groceries", 250, 1200, 20, 200),
    ("Wheat Flour", "Groceries", 100, 600, 20, 200),
    ("Cooking Oil", "Groceries", 120, 900, 20, 200),
    ("Coffee Powder", "Groceries", 150, 1000, 15, 150),
    ("Breakfast Cereal", "Groceries", 180, 900, 15, 150),

    ("Office Chair", "Furniture", 3500, 18000, 5, 50),
    ("Study Table", "Furniture", 2500, 15000, 5, 50),
    ("Bookshelf", "Furniture", 3000, 16000, 5, 40),
    ("Sofa", "Furniture", 18000, 60000, 2, 20),
    ("Dining Table", "Furniture", 12000, 50000, 2, 25),

    ("Remote Car", "Toys", 700, 3500, 10, 100),
    ("Building Blocks", "Toys", 500, 3000, 10, 100),
    ("Board Game", "Toys", 400, 2500, 10, 100),
    ("Toy Robot", "Toys", 800, 5000, 8, 80),
    ("Puzzle Set", "Toys", 250, 1500, 15, 150),

    ("Car Cover", "Automotive", 800, 3500, 10, 80),
    ("Bike Helmet", "Automotive", 900, 5000, 10, 100),
    ("Engine Oil", "Automotive", 500, 2500, 15, 120),
    ("Car Vacuum", "Automotive", 1200, 6000, 5, 60),
    ("Dash Camera", "Automotive", 2500, 12000, 5, 50),

    ("Running Shoes", "Footwear", 1200, 7000, 10, 100),
    ("Casual Shoes", "Footwear", 900, 5000, 10, 100),
    ("Sports Sandals", "Footwear", 600, 3000, 15, 120),
    ("Formal Shoes", "Footwear", 1200, 6000, 10, 80),
    ("Slippers", "Footwear", 150, 1200, 20, 200),

    ("Necklace", "Jewelry", 1000, 15000, 5, 50),
    ("Bracelet", "Jewelry", 500, 8000, 5, 60),
    ("Ring", "Jewelry", 800, 12000, 5, 50),
    ("Earrings", "Jewelry", 400, 6000, 8, 80),
    ("Pendant", "Jewelry", 600, 9000, 5, 60),

    ("Notebook", "Stationery", 50, 300, 30, 300),
    ("Ball Pen Set", "Stationery", 80, 500, 30, 300),
    ("Marker Set", "Stationery", 100, 600, 20, 250),
    ("Drawing Book", "Stationery", 80, 400, 20, 250),
    ("File Folder", "Stationery", 30, 250, 30, 300),

    ("Non Stick Pan", "Kitchen", 700, 3500, 10, 100),
    ("Pressure Cooker", "Kitchen", 1200, 5000, 8, 80),
    ("Knife Set", "Kitchen", 500, 3000, 10, 100),
    ("Dinner Set", "Kitchen", 1000, 6000, 5, 60),
    ("Storage Container", "Kitchen", 200, 1800, 15, 150),

    ("Gaming Mouse", "Gaming", 800, 5000, 10, 100),
    ("Mechanical Keyboard", "Gaming", 1800, 10000, 5, 70),
    ("Game Controller", "Gaming", 1500, 7000, 5, 70),
    ("Gaming Headset", "Gaming", 1500, 8000, 5, 70),
    ("Mouse Pad", "Gaming", 200, 2000, 15, 150),
]


PAYMENT_METHODS = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Cash on Delivery",
]


ORDER_STATUSES = [
    ("Delivered", 55),
    ("Shipped", 20),
    ("Processing", 15),
    ("Cancelled", 10),
]


REVIEW_TEXTS = {
    1: [
        "Very disappointing",
        "Not satisfied with the product",
    ],
    2: [
        "Could be better",
        "Below expectations",
    ],
    3: [
        "Average product",
        "It is okay for the price",
    ],
    4: [
        "Good product",
        "Worth the money",
        "Satisfied with the purchase",
    ],
    5: [
        "Excellent quality",
        "Very good product",
        "Amazing experience",
    ],
}


def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def weighted_choice(items):
    values = [item[0] for item in items]
    weights = [item[1] for item in items]
    return random.choices(values, weights=weights, k=1)[0]


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
        "categories",
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

    # ---------------------------------------------------------
    # CATEGORIES
    # ---------------------------------------------------------

    print("Creating categories...")

    category_ids = {}

    for category_name in CATEGORIES:
        cursor.execute(
            """
            INSERT INTO categories (category_name)
            VALUES (%s)
            """,
            (category_name,),
        )

        category_ids[category_name] = cursor.lastrowid

    # ---------------------------------------------------------
    # CUSTOMERS
    # ---------------------------------------------------------

    print("Creating customers...")

    customer_ids = []
    customer_registration_dates = {}

    for i in range(100):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        email = (
            f"{first_name.lower()}."
            f"{last_name.lower()}."
            f"{i + 1}@example.com"
        )

        phone = f"9{random.randint(100000000, 999999999)}"

        city, state = random.choice(CITY_STATE_PAIRS)

        registration_date = random_date(
            datetime(2024, 1, 1),
            datetime(2025, 12, 31),
        ).date()

        cursor.execute(
            """
            INSERT INTO customers
            (
                first_name,
                last_name,
                email,
                phone,
                city,
                state,
                registration_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                first_name,
                last_name,
                email,
                phone,
                city,
                state,
                registration_date,
            ),
        )

        customer_id = cursor.lastrowid

        customer_ids.append(customer_id)
        customer_registration_dates[customer_id] = registration_date

    # ---------------------------------------------------------
    # PRODUCTS
    # ---------------------------------------------------------

    print("Creating products...")

    product_ids = []

    for (
        product_name,
        category_name,
        minimum_price,
        maximum_price,
        minimum_stock,
        maximum_stock,
    ) in PRODUCTS:

        category_id = category_ids[category_name]

        price = round(
            random.uniform(
                minimum_price,
                maximum_price,
            ),
            2,
        )

        stock_quantity = random.randint(
            minimum_stock,
            maximum_stock,
        )

        created_date = random_date(
            datetime(2024, 1, 1),
            datetime(2025, 12, 31),
        ).date()

        cursor.execute(
            """
            INSERT INTO products
            (
                product_name,
                category_id,
                price,
                stock_quantity,
                created_date
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                product_name,
                category_id,
                price,
                stock_quantity,
                created_date,
            ),
        )

        product_ids.append(
            {
                "product_id": cursor.lastrowid,
                "price": price,
                "created_date": created_date,
            }
        )

    # ---------------------------------------------------------
    # ORDERS + ORDER ITEMS
    # ---------------------------------------------------------

    print("Creating orders and order items...")

    order_ids = []

    for _ in range(500):

        customer_id = random.choice(customer_ids)

        registration_date = customer_registration_dates[
            customer_id
        ]

        earliest_order_date = max(
            registration_date,
            datetime(2025, 1, 1).date(),
        )

        order_date = random_date(
            datetime.combine(
                earliest_order_date,
                datetime.min.time(),
            ),
            datetime(2026, 9, 30),
        )

        status = weighted_choice(ORDER_STATUSES)

        available_products = [
            product
            for product in product_ids
            if product["created_date"] <= order_date.date()
        ]

        selected_products = random.sample(
            available_products,
            random.randint(1, 4),
        )

        order_items_data = []
        total_amount = 0

        for product in selected_products:

            quantity = random.randint(1, 5)

            order_items_data.append(
                (
                    product["product_id"],
                    quantity,
                    product["price"],
                )
            )

            total_amount += (
                quantity * product["price"]
            )

        total_amount = round(total_amount, 2)

        cursor.execute(
            """
            INSERT INTO orders
            (
                customer_id,
                order_date,
                status,
                total_amount
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                customer_id,
                order_date,
                status,
                total_amount,
            ),
        )

        order_id = cursor.lastrowid
        order_ids.append(order_id)

        for (
            product_id,
            quantity,
            unit_price,
        ) in order_items_data:

            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                ),
            )

    # ---------------------------------------------------------
    # PAYMENTS
    # ---------------------------------------------------------

    print("Creating payments...")

    for order_id in order_ids:

        cursor.execute(
            """
            SELECT
                order_date,
                total_amount,
                status
            FROM orders
            WHERE order_id = %s
            """,
            (order_id,),
        )

        order_date, total_amount, status = cursor.fetchone()

        payment_date = order_date + timedelta(
            days=random.randint(0, 3),
            hours=random.randint(0, 8),
        )

        payment_method = random.choice(
            PAYMENT_METHODS
        )

        if status == "Cancelled":
            payment_status = "Failed"
            amount = 0
        else:
            payment_status = "Completed"
            amount = total_amount

        cursor.execute(
            """
            INSERT INTO payments
            (
                order_id,
                payment_date,
                amount,
                payment_method,
                payment_status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                order_id,
                payment_date,
                amount,
                payment_method,
                payment_status,
            ),
        )

    # ---------------------------------------------------------
    # REVIEWS
    # ---------------------------------------------------------

    print("Creating reviews...")

    cursor.execute(
        """
        SELECT DISTINCT
            o.customer_id,
            oi.product_id,
            o.order_date
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        WHERE o.status != 'Cancelled'
        """
    )

    purchase_records = cursor.fetchall()

    random.shuffle(purchase_records)

    review_count = min(
        300,
        len(purchase_records),
    )

    used_review_pairs = set()

    created_reviews = 0

    for (
        customer_id,
        product_id,
        order_date,
    ) in purchase_records:

        if created_reviews >= review_count:
            break

        pair = (
            customer_id,
            product_id,
        )

        if pair in used_review_pairs:
            continue

        used_review_pairs.add(pair)

        rating = random.choices(
            [1, 2, 3, 4, 5],
            weights=[5, 8, 17, 35, 35],
            k=1,
        )[0]

        review_text = random.choice(
            REVIEW_TEXTS[rating]
        )

        review_date = (
            order_date
            + timedelta(
                days=random.randint(1, 30)
            )
        ).date()

        if review_date > datetime(2026, 9, 30).date():
            review_date = datetime(2026, 9, 30).date()

        cursor.execute(
            """
            INSERT INTO reviews
            (
                product_id,
                customer_id,
                rating,
                review_text,
                review_date
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                product_id,
                customer_id,
                rating,
                review_text,
                review_date,
            ),
        )

        created_reviews += 1

    # ---------------------------------------------------------
    # COMMIT
    # ---------------------------------------------------------

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
        "reviews",
    ]

    for table in tables:
        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cursor.fetchone()[0]

        print(
            f"{table}: {count} rows"
        )

    cursor.close()
    connection.close()

    print()
    print("MySQL connection closed.")


if __name__ == "__main__":
    main()