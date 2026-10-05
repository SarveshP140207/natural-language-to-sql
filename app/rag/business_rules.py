BUSINESS_RULES = [
    {
        "rule_id": "revenue_001",
        "title": "Revenue excludes cancelled orders",
        "description": (
            "When calculating revenue, sales, or spending, "
            "cancelled orders should normally be excluded."
        ),
        "tables": ["orders"],
        "columns": ["status", "total_amount"],
    },
    {
        "rule_id": "payment_001",
        "title": "Cancelled payments are not completed payments",
        "description": (
            "Payments with payment_status indicating failure or cancellation "
            "should not be treated as successful payments."
        ),
        "tables": ["payments"],
        "columns": ["payment_status", "amount"],
    },
    {
        "rule_id": "order_001",
        "title": "Order items belong to orders",
        "description": (
            "order_items.order_id references orders.order_id. "
            "Use this relationship when calculating product sales from orders."
        ),
        "tables": ["orders", "order_items"],
        "columns": ["order_id"],
    },
    {
        "rule_id": "product_001",
        "title": "Products belong to categories",
        "description": (
            "products.category_id references categories.category_id. "
            "Use this relationship when analyzing products by category."
        ),
        "tables": ["products", "categories"],
        "columns": ["category_id"],
    },
]