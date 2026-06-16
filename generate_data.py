import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)

conn = sqlite3.connect("customer_360.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS Fact_Orders;
DROP TABLE IF EXISTS Fact_Order_Items;
DROP TABLE IF EXISTS Dim_Customers;
DROP TABLE IF EXISTS Dim_Products;
DROP TABLE IF EXISTS Dim_Regions;
DROP TABLE IF EXISTS Dim_Dates;

CREATE TABLE Dim_Regions (
    region_id   INTEGER PRIMARY KEY,
    region_name TEXT,
    country     TEXT
);

CREATE TABLE Dim_Customers (
    customer_id      INTEGER PRIMARY KEY,
    first_name       TEXT,
    last_name        TEXT,
    email            TEXT,
    region_id        INTEGER,
    join_date        TEXT,
    customer_segment TEXT,
    age              INTEGER,
    gender           TEXT,
    FOREIGN KEY (region_id) REFERENCES Dim_Regions(region_id)
);

CREATE TABLE Dim_Products (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT,
    category     TEXT,
    unit_price   REAL,
    cost         REAL,
    brand        TEXT
);

CREATE TABLE Dim_Dates (
    date_id    TEXT PRIMARY KEY,
    year       INTEGER,
    month      INTEGER,
    quarter    INTEGER,
    month_name TEXT
);

CREATE TABLE Fact_Orders (
    order_id     INTEGER PRIMARY KEY,
    customer_id  INTEGER,
    date_id      TEXT,
    region_id    INTEGER,
    status       TEXT,
    total_amount REAL,
    FOREIGN KEY (customer_id) REFERENCES Dim_Customers(customer_id),
    FOREIGN KEY (date_id)     REFERENCES Dim_Dates(date_id),
    FOREIGN KEY (region_id)   REFERENCES Dim_Regions(region_id)
);

CREATE TABLE Fact_Order_Items (
    item_id     INTEGER PRIMARY KEY,
    order_id    INTEGER,
    product_id  INTEGER,
    quantity    INTEGER,
    unit_price  REAL,
    total_price REAL,
    FOREIGN KEY (order_id)   REFERENCES Fact_Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Dim_Products(product_id)
);
""")

regions = [
    (1,"Northeast","USA"),(2,"Southeast","USA"),
    (3,"Midwest","USA"),(4,"West Coast","USA"),
    (5,"Southwest","USA"),(6,"Mid-Atlantic","USA"),
]
cur.executemany("INSERT INTO Dim_Regions VALUES (?,?,?)", regions)

products = [
    (1,"Vitamin C Serum","Skincare",68.99,18.00,"GlowLab"),
    (2,"Hydrating Face Cream","Skincare",54.99,14.00,"GlowLab"),
    (3,"Retinol Night Cream","Skincare",89.99,24.00,"DermaPure"),
    (4,"Matte Lipstick Set","Makeup",34.99,8.00,"ColorPop"),
    (5,"Foundation SPF 30","Makeup",44.99,12.00,"ColorPop"),
    (6,"Eyeshadow Palette","Makeup",59.99,16.00,"ColorPop"),
    (7,"Argan Oil Hair Mask","Haircare",39.99,10.00,"LuxeHair"),
    (8,"Keratin Shampoo","Haircare",29.99,7.00,"LuxeHair"),
    (9,"Leave-In Conditioner","Haircare",24.99,6.00,"LuxeHair"),
    (10,"Rose Body Scrub","Body Care",32.99,8.00,"PureSkin"),
    (11,"Lavender Body Lotion","Body Care",27.99,6.00,"PureSkin"),
    (12,"Luxury Perfume","Fragrance",129.99,40.00,"Essence"),
    (13,"Mini Perfume Set","Fragrance",79.99,22.00,"Essence"),
    (14,"Jade Facial Roller","Tools",24.99,5.00,"BeautyTools"),
    (15,"Gua Sha Stone Set","Tools",19.99,4.00,"BeautyTools"),
]
cur.executemany("INSERT INTO Dim_Products VALUES (?,?,?,?,?,?)", products)

month_names = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
dates = []
for year in [2024, 2025, 2026]:
    for month in range(1, 13):
        date_id = f"{year}-{month:02d}"
        quarter = (month - 1) // 3 + 1
        dates.append((date_id, year, month, quarter, month_names[month-1]))
cur.executemany("INSERT OR IGNORE INTO Dim_Dates VALUES (?,?,?,?,?)", dates)

first_names = ["James","Maria","David","Sarah","Michael","Emily","Robert",
               "Jessica","William","Ashley","John","Amanda","Christopher",
               "Stephanie","Daniel","Melissa","Matthew","Jennifer","Andrew","Lisa"]
last_names  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller",
               "Davis","Wilson","Taylor","Anderson","Thomas","Jackson","White",
               "Harris","Martin","Thompson","Moore","Young","Allen"]
segments = ["Premium","Premium","Regular","Regular","Budget"]
genders  = ["Female","Female","Female","Male","Non-Binary"]

# Generate 600 customers with realistic attributes
customers_data = []
for i in range(1, 601):
    fn  = random.choice(first_names)
    ln  = random.choice(last_names)
    rid = random.randint(1, 6)
    days_ago = random.randint(30, 1095)
    jd  = (datetime(2026,6,15) - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    seg = random.choice(segments)
    age = random.randint(18, 65)
    gender = random.choice(genders)
    customers_data.append((i, fn, ln,
        f"{fn.lower()}.{ln.lower()}{i}@email.com",
        rid, jd, seg, age, gender))
cur.executemany("INSERT INTO Dim_Customers VALUES (?,?,?,?,?,?,?,?,?)",
                customers_data)

order_id = 1
item_id  = 1
orders_data = []
items_data  = []

# Order frequency varies by segment to simulate realistic RFM buying patterns
for cid in range(1, 601):
    seg = customers_data[cid-1][6]
    # Get the customer's region_id from position 4 in customers_data
    customer_rid = customers_data[cid-1][4]

    if seg == "Premium":
        num_orders = random.randint(8, 20)
    elif seg == "Regular":
        num_orders = random.randint(3, 8)
    else:
        num_orders = random.randint(1, 3)

    for _ in range(num_orders):
        days_ago = random.randint(1, 730)
        order_date = datetime(2026,6,15) - timedelta(days=days_ago)
        date_id = order_date.strftime("%Y-%m")

        # Weighted toward Completed to reflect realistic fulfillment rates
        status = random.choices(
            ["Completed","Completed","Completed","Returned","Cancelled"], k=1
        )[0]

        order_total = 0
        num_items = random.randint(1, 4)
        order_items_temp = []

        for _ in range(num_items):
            pid   = random.randint(1, 15)
            price = products[pid-1][3]
            qty   = random.randint(1, 3) if seg == "Premium" else 1
            total = round(price * qty, 2)
            order_total += total
            order_items_temp.append((item_id, order_id, pid, qty,
                                     price, total))
            item_id += 1

        orders_data.append((order_id, cid, date_id, customer_rid,
                            status, round(order_total, 2)))
        items_data.extend(order_items_temp)
        order_id += 1

cur.executemany("INSERT INTO Fact_Orders VALUES (?,?,?,?,?,?)", orders_data)
cur.executemany("INSERT INTO Fact_Order_Items VALUES (?,?,?,?,?,?)", items_data)

conn.commit()
conn.close()
print(f"Data warehouse created!")
print(f"Customers: 600")
print(f"Orders: {len(orders_data)}")
print(f"Order Items: {len(items_data)}")