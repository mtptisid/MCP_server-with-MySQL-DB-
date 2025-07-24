# MCP Server: MySQL Database Integration

This README explains how the MCP server integrates MySQL tables as resources, previews their schema and sample data, and provides commands for setup and testing.

## Overview
- The MCP server lists notes, files, and MySQL tables as resources.
- MySQL tables are shown with their schema and up to 3 rows of sample data.
- All endpoints are accessible via HTTP POST to `/mcp`.

## How MySQL Tables Are Added as Resources

### 1. Code Location
- All logic is in `src/simple_mcp_server/server.py`.

### 2. Procedure
- The function `handle_list_resources()` is decorated with `@server.list_resources()` and is called when the MCP client requests resources.
- Inside this function:
  1. A connection to MySQL is established using `mysql.connector.connect(**MYSQL_CONFIG)`.
  2. All table names are fetched with `SHOW TABLES;`.
  3. For each table:
     - The schema is fetched using `DESCRIBE <table>;`.
     - Up to 3 rows of sample data are fetched using `SELECT * FROM <table> LIMIT 3;`.
     - A resource is created with:
       - `uri=AnyUrl(f"mysql://localhost/bank/{table}")`
       - `name=f"MySQL Table: {table}"`
       - `description=f"Table {table} schema: {schema}\nSample data:\n{data_preview}"`
       - `mimeType="application/sql"`
  4. If any error occurs, a fallback resource is added with a connection error message.

### 3. Key Code Snippet
```python
try:
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        cursor.execute(f"DESCRIBE {table};")
        columns = cursor.fetchall()
        schema = ', '.join([f"{col[0]} {col[1]}" for col in columns])
        cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
        rows = cursor.fetchall()
        data_preview = '\n'.join([str(row) for row in rows]) if rows else 'No data.'
        resources.append(
            types.Resource(
                uri=AnyUrl(f"mysql://localhost/bank/{table}"),
                name=f"MySQL Table: {table}",
                description=f"Table {table} schema: {schema}\nSample data:\n{data_preview}",
                mimeType="application/sql",
            )
        )
    cursor.close()
    conn.close()
except Exception as e:
    logger.error(f"MySQL error: {e}")
    resources.append(
        types.Resource(
            uri=AnyUrl("mysql://localhost/bank"),
            name="Bank MySQL Database",
            description="MySQL database for bank customer and transaction details (connection error)",
            mimeType="application/sql",
        )
    )
```

### 4. How Schema and Data Are Shown
- The schema is a comma-separated list of column names and types.
- The sample data is up to 3 rows, each shown as a tuple.
- Both are included in the resource's description field.

## MySQL Setup
1. **Install MySQL Server** (if not already installed):
   ```bash
   sudo apt-get update
   sudo apt-get install mysql-server
   ```
2. **Start MySQL Service:**
   ```bash
   sudo service mysql start
   ```
3. **Create Database and Tables:**
   ```bash
   sudo mysql -u root <<EOF
   CREATE DATABASE IF NOT EXISTS bank;
   USE bank;
   CREATE TABLE IF NOT EXISTS customers (
     id INT PRIMARY KEY AUTO_INCREMENT,
     name VARCHAR(100),
     balance DECIMAL(10,2)
   );
   CREATE TABLE IF NOT EXISTS transactions (
     id INT PRIMARY KEY AUTO_INCREMENT,
     customer_id INT,
     amount DECIMAL(10,2),
     type VARCHAR(10),
     FOREIGN KEY (customer_id) REFERENCES customers(id)
   );
   EOF
   ```
4. **Insert Sample Data:**
   ```bash
   sudo mysql -u root <<EOF
   USE bank;
   INSERT INTO customers (name, balance) VALUES ('Alice', 1000.00), ('Bob', 500.00), ('Charlie', 750.00);
   INSERT INTO transactions (customer_id, amount, type) VALUES (1, 200.00, 'deposit'), (2, 50.00, 'withdrawal'), (3, 100.00, 'deposit');
   EOF
   ```

## MCP Server Code (Key Parts)
- Uses `mysql-connector-python` to connect to MySQL.
- Lists tables, fetches schema and up to 3 rows for preview (see above for code).

## Testing with curl
- **List Resources:**
  ```bash
  curl -X POST http://localhost:8000/mcp \
    -H 'Content-Type: application/json' \
    -d '{"jsonrpc":"2.0","id":1,"method":"listResources"}'
  ```
- **Expected Output:**
  - Notes, files, and MySQL tables listed as resources.
  - MySQL tables show schema and sample data in their description.

## Troubleshooting
- If you see a MySQL connection error, check:
  - MySQL service is running (`sudo service mysql status`).
  - Python package `mysql-connector-python` is installed:
    ```bash
    pip install mysql-connector-python
    ```
  - Database credentials in `server.py` match your MySQL setup.

## References
- [Model Context Protocol](https://modelcontextprotocol.io/llms-full.txt)
- [MCP Python SDK Example](https://github.com/modelcontextprotocol/create-python-server)

---
This README documents the MCP server's MySQL integration, setup, and testing. For further details, see `server.py`.
