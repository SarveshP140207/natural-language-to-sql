import json

from app.database.introspector import get_database_schema


try:
    schema = get_database_schema()

    print("Database introspection successful!\n")
    print(json.dumps(schema, indent=4))

except Exception as e:
    print("Database introspection failed!")
    print(f"Error: {e}")