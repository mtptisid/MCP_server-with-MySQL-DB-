# simple-mcp-server MCP server

A simple MCP server example

## Components

### MySQL Database Integration

The server integrates MySQL tables as MCP resources, showing their schema and sample data. This enables you to preview database contents directly from the MCP resource listing.

#### Key Implementation File
- **`src/simple_mcp_server/server.py`**: All resource logic, including MySQL integration, is implemented here.

#### How It Works
- The server connects to MySQL using `mysql-connector-python`.
- It lists all tables in the `bank` database.
- For each table, it fetches the schema (column names and types) and up to 3 rows of sample data.
- Each table is registered as a resource with:
  - URI: `mysql://localhost/bank/<table>`
  - Name: `MySQL Table: <table>`
  - Description: Table schema and sample data preview
  - MIME type: `application/sql`

#### Example Code Snippet
```python
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
```

#### Setup Instructions
1. **Install MySQL Server:**
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
5. **Install Python MySQL Connector:**
   ```bash
   pip install mysql-connector-python
   ```

#### Testing with curl
- **List Resources:**
  ```bash
  curl -X POST http://localhost:8000/mcp \
    -H 'Content-Type: application/json' \
    -d '{"jsonrpc":"2.0","id":1,"method":"listResources"}'
  ```
- **Expected Output:**
  - Notes, files, and MySQL tables listed as resources.
  - MySQL tables show schema and sample data in their description.

#### Troubleshooting
- If you see a MySQL connection error, check:
  - MySQL service is running (`sudo service mysql status`).
  - Python package `mysql-connector-python` is installed.
  - Database credentials in `server.py` match your MySQL setup.

#### References
- [Model Context Protocol](https://modelcontextprotocol.io/llms-full.txt)
- [MCP Python SDK Example](https://github.com/modelcontextprotocol/create-python-server)

### Resources

The server implements a simple note storage system with:
- Custom note:// URI scheme for accessing individual notes
- Each note resource has a name, description and text/plain mimetype
- MySQL tables as resources (see above for details)

### Prompts

The server provides a single prompt:
- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools

The server implements one tool:
- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration

### MySQL
- Database: `bank`
- Tables: `customers`, `transactions`
- Credentials: See `MYSQL_CONFIG` in `src/simple_mcp_server/server.py`

[TODO: Add other configuration details specific to your implementation]

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ...existing code...
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ...existing code...
</details>

## Development

### Building and Publishing

...existing code...

### Debugging

...existing code...

### Screenshots

<img width="1440" height="900" alt="Screenshot 1947-05-03 at 12 25 14 AM" src="https://github.com/user-attachments/assets/be37ed80-816c-4c79-aaac-cb0a0927c78b" />


<img width="1440" height="900" alt="Screenshot 1947-05-03 at 12 25 30 AM" src="https://github.com/user-attachments/assets/22fdda7e-ca8f-440e-b577-aa2428c35e97" />
