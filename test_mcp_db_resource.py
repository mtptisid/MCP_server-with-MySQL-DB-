import requests
from tabulate import tabulate
import json
import ast
import re

def get_resources():
    url = "http://localhost:8000/mcp"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "listResources"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def safe_parse_tuple(row):
    # Remove Decimal and datetime wrappers for safe eval
    row = re.sub(r"Decimal\('([0-9.]+)'\)", r"\1", row)
    row = re.sub(r"datetime\.datetime\([^)]+\)", "'datetime'", row)
    try:
        return ast.literal_eval(row)
    except Exception:
        return [row]

def print_mysql_tables(resources):
    for res in resources:
        if res["mimeType"] == "application/sql":
            print(f"\nResource: {res['name']}")
            print(f"URI: {res['uri']}")
            desc = res["description"]
            # Try to split schema and sample data
            if "Sample data:" in desc:
                schema, sample = desc.split("Sample data:", 1)
                print(f"Schema: {schema.strip()}")
                print("Sample data:")
                # Try to parse sample data as rows
                rows = [row.strip() for row in sample.strip().split("\n") if row.strip()]
                if rows and rows[0] != "No data.":
                    # Try to print as table if possible
                    parsed = [safe_parse_tuple(r) for r in rows]
                    print(tabulate(parsed, tablefmt="grid"))
                else:
                    print("No data.")
            else:
                print(desc)

def main():
    result = get_resources()
    resources = result.get("result", [])
    print_mysql_tables(resources)

if __name__ == "__main__":
    main()
