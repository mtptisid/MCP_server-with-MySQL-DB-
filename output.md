# Terminal Output: MCP Server & MySQL Resource Integration

---

## 1. Initial Setup & Error
```bash
(.venv) $ pkill -f uvicorn
(.venv) $ curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":51,"method":"listResources"}' http://localhost:8000/mcp
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

## 2. List Resources (No DB Data)
```bash
(.venv) $ curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":61,"method":"listResources"}' http://localhost:8000/mcp
```
**Response:**
```json
{"jsonrpc":"2.0","id":61,"result":[
  {"name":"Note: example", ...},
  {"name":"File: sample2.txt", ...},
  {"name":"File: sample1.txt", ...},
  {"name":"Bank MySQL Database", "description":"MySQL database for bank customer and transaction details (connection error)", ...}
]}
```

## 3. Fix MySQL Credentials
```bash
(.venv) $ sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY ''; FLUSH PRIVILEGES;"
```

## 4. List Resources (DB Schema Only)
```bash
(.venv) $ curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":71,"method":"listResources"}' http://localhost:8000/mcp
```
**Response:**
```json
{"jsonrpc":"2.0","id":71,"result":[
  {"name":"Note: example", ...},
  {"name":"File: sample2.txt", ...},
  {"name":"File: sample1.txt", ...},
  {"name":"MySQL Table: customer", "description":"Table customer schema: id int, name varchar(100), email varchar(100), phone varchar(20), address varchar(255)", ...},
  {"name":"MySQL Table: transaction", "description":"Table transaction schema: id int, customer_id int, amount decimal(10,2), type enum('deposit','withdrawal','transfer'), timestamp datetime", ...}
]}
```

## 5. Insert Sample Data
```bash
(.venv) $ sudo mysql -u root bank -e "INSERT INTO customer (name, email, phone, address) VALUES ('Alice', 'alice@example.com', '1234567890', 'Wonderland'), ('Bob', 'bob@example.com', '0987654321', 'Builder St'); INSERT INTO transaction (customer_id, amount, type, timestamp) VALUES (1, 100.00, 'deposit', NOW()), (2, 50.00, 'withdrawal', NOW());"
```

## 6. List Resources (With Sample Data)
```bash
(.venv) $ curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":81,"method":"listResources"}' http://localhost:8000/mcp
```
**Response:**
```json
{
  "jsonrpc":"2.0",
  "id":81,
  "result":[
    {"name":"Note: example", ...},
    {"name":"File: sample2.txt", ...},
    {"name":"File: sample1.txt", ...},
    {"name":"MySQL Table: customer", "description":"Table customer schema: id int, name varchar(100), email varchar(100), phone varchar(20), address varchar(255)\nSample data:\n(1, 'Alice', 'alice@example.com', '1234567890', 'Wonderland')\n(2, 'Bob', 'bob@example.com', '0987654321', 'Builder St')", ...},
    {"name":"MySQL Table: transaction", "description":"Table transaction schema: id int, customer_id int, amount decimal(10,2), type enum('deposit','withdrawal','transfer'), timestamp datetime\nSample data:\n(1, 1, Decimal('100.00'), 'deposit', datetime.datetime(2025, 7, 24, 18, 30, 33))\n(2, 2, Decimal('50.00'), 'withdrawal', datetime.datetime(2025, 7, 24, 18, 30, 33))", ...}
  ]
}
```

## 7. MySQL Table Resources Documentation
```
Resource: MySQL Table: customer
URI: mysql://localhost/bank/customer
Schema: Table customer schema: id int, name varchar(100), email varchar(100), phone varchar(20), address varchar(255)
Sample data:
+---+-------+-------------------+------------+------------+
| 1 | Alice | alice@example.com | 1234567890 | Wonderland |
+---+-------+-------------------+------------+------------+
| 2 | Bob   | bob@example.com   | 0987654321 | Builder St |
+---+-------+-------------------+------------+------------+

Resource: MySQL Table: customers
URI: mysql://localhost/bank/customers
Schema: Table customers schema: id int, name varchar(100), balance decimal(10,2)
Sample data:
+---+-------+------+ 
| 1 | David | 1200 |
+---+-------+------+
| 2 | Eva   |  300 |
+---+-------+------+
| 3 | Frank |  800 |
+---+-------+------+

Resource: MySQL Table: transaction
URI: mysql://localhost/bank/transaction
Schema: Table transaction schema: id int, customer_id int, amount decimal(10,2), type enum('deposit','withdrawal','transfer'), timestamp datetime
Sample data:
+---+---+-----+------------+----------+
| 1 | 1 | 100 | deposit    | datetime |
+---+---+-----+------------+----------+
| 2 | 2 |  50 | withdrawal | datetime |
+---+---+-----+------------+----------+

Resource: MySQL Table: transactions
URI: mysql://localhost/bank/transactions
Schema: Table transactions schema: id int, customer_id int, amount decimal(10,2), type varchar(10)
Sample data:
+---+---+-----+------------+
| 1 | 1 | 500 | deposit    |
+---+---+-----+------------+
| 2 | 2 | 100 | withdrawal |
+---+---+-----+------------+
| 3 | 3 | 200 | deposit    |
+---+---+-----+------------+
```

---

# Summary
- Shows step-by-step terminal commands and their results for MCP server and MySQL resource integration.
- Demonstrates how MySQL tables appear as resources, including schema and sample data.