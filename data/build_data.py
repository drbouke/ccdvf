"""Builds the Acme data set used by every example: an online electronics store.

    python data/build_data.py        (re-creates data/store.db; the same seed gives the same data every time)

Tables: customers, products, orders, order_items, payments, shipments, tracking_events, refunds.
The data is generated, but shaped like a real store: about 150 customers, 500 orders over three months, card and
bank transfer payments (some charged twice), courier scans with delays and failed deliveries, and earlier refunds.
"""
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / 'store.db'
rng = random.Random(2026)

FIRST = ['Alice', 'Henry', 'Nora', 'Adam', 'Fiona', 'Zack', 'Susan', 'Ian', 'Wendy', 'Jason', 'Megan', 'Kevin',
         'Paula', 'Aaron', 'Karen', 'Ryan', 'David', 'Emma', 'Hannah', 'Frank', 'Laura', 'Charles', 'Diana', 'Steven']
LAST = {'Alice': 'Rahman', 'Henry': 'Ismail', 'Nora': 'Hassan', 'Adam': 'Yusof', 'Fiona': 'Aziz', 'Zack': 'Kamal',
        'Susan': 'Omar', 'Ian': 'Hamid', 'Wendy': 'Tan', 'Jason': 'Lim', 'Megan': 'Wong', 'Kevin': 'Lee',
        'Paula': 'Nair', 'Aaron': 'Pillai', 'Karen': 'Raj', 'Ryan': 'Kumar', 'David': 'Lee', 'Emma': 'Ng',
        'Hannah': 'Ahmad', 'Frank': 'Salleh', 'Laura': 'Zainal', 'Charles': 'Ong', 'Diana': 'Menon', 'Steven': 'Krishnan'}
CITIES = ['Central', 'Northside', 'Eastside', 'Westside', 'Southside', 'Lakeside', 'Hillside', 'Riverside',
          'Bayview', 'Midtown', 'Uptown', 'Harbor']
PRODUCTS = [
    ('P-101', 'Aurora 2-in-1 Blender 1.5L', 'kitchen', 289.00), ('P-102', 'Kettle Pro 1.7L Stainless', 'kitchen', 129.00),
    ('P-103', 'Rice Cooker Smart 1.8L', 'kitchen', 359.00), ('P-104', 'Air Fryer XL 6L', 'kitchen', 499.00),
    ('P-201', 'Nova Wireless Earbuds', 'audio', 199.00), ('P-202', 'Pulse Noise-Cancelling Headphones', 'audio', 649.00),
    ('P-203', 'Beat Mini Bluetooth Speaker', 'audio', 159.00), ('P-301', 'Volt 20000mAh Power Bank', 'mobile', 119.00),
    ('P-302', 'Swift 65W GaN Charger', 'mobile', 139.00), ('P-303', 'Shield Phone Case (iPhone 17)', 'mobile', 59.00),
    ('P-401', 'Lumen 27in 4K Monitor', 'computing', 1299.00), ('P-402', 'Keystone Mechanical Keyboard', 'computing', 389.00),
    ('P-403', 'Glide Wireless Mouse', 'computing', 99.00), ('P-404', 'Dock 11-in-1 USB-C Hub', 'computing', 229.00),
    ('P-501', 'Breeze Smart Fan 16in', 'home', 269.00), ('P-502', 'Pure Air Purifier H13', 'home', 899.00),
    ('P-503', 'Glow Smart Bulb (4-pack)', 'home', 149.00), ('P-504', 'Guard Wi-Fi Camera 2K', 'home', 239.00),
]
COURIERS = ['FastShip', 'QuickParcel', 'ParcelOne', 'Global Express']
HUBS = ['Eastside hub', 'Central hub', 'Lakeside hub', 'Southside hub', 'Bayview hub', 'Midtown hub']


def ts(d):
    return d.strftime('%Y-%m-%d %H:%M')


def build():
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    c = con.cursor()
    c.executescript('''
    CREATE TABLE customers (customer_id TEXT PRIMARY KEY, name TEXT, email TEXT, phone TEXT, city TEXT, joined TEXT, tier TEXT);
    CREATE TABLE products (product_id TEXT PRIMARY KEY, name TEXT, category TEXT, price REAL);
    CREATE TABLE orders (order_id TEXT PRIMARY KEY, customer_id TEXT, placed_at TEXT, status TEXT, total REAL,
                         ship_city TEXT, delivered_at TEXT);
    CREATE TABLE order_items (order_id TEXT, product_id TEXT, qty INTEGER, unit_price REAL);
    CREATE TABLE payments (payment_id TEXT PRIMARY KEY, order_id TEXT, method TEXT, amount REAL, status TEXT, paid_at TEXT);
    CREATE TABLE shipments (order_id TEXT PRIMARY KEY, courier TEXT, tracking_no TEXT, shipped_at TEXT, promised_by TEXT);
    CREATE TABLE tracking_events (order_id TEXT, at TEXT, location TEXT, event TEXT);
    CREATE TABLE refunds (refund_id TEXT PRIMARY KEY, order_id TEXT, amount REAL, reason TEXT, status TEXT, created_at TEXT,
                          approved_by TEXT);
    ''')
    c.executemany('INSERT INTO products VALUES (?,?,?,?)', PRODUCTS)

    start = datetime(2026, 8, 1, 9, 0)
    customers = []
    for i in range(150):
        first = rng.choice(FIRST)
        cid = 'C-%04d' % (1100 + i)
        email = '%s.%s%d@%s' % (first.lower().replace(' ', ''), LAST[first].lower(), rng.randint(1, 99),
                                rng.choice(['example.com', 'example.org', 'example.net', 'mail.example']))
        customers.append((cid, '%s %s' % (first, LAST[first]), email, '555-01%d-%03d %04d' % (rng.randint(0, 9), rng.randint(100, 999), rng.randint(0, 9999)),
                          rng.choice(CITIES), ts(start - timedelta(days=rng.randint(30, 900))), rng.choice(['standard'] * 8 + ['gold'] * 2)))
    c.executemany('INSERT INTO customers VALUES (?,?,?,?,?,?,?)', customers)

    now = datetime(2026, 10, 31, 18, 0)
    for n in range(500):
        oid = 'ord_%05d' % (20500 + n * 3 + rng.randint(0, 2))
        cust = rng.choice(customers)
        placed = start + timedelta(minutes=rng.randint(0, int((now - start).total_seconds() // 60) - 60 * 24))
        items = rng.sample(PRODUCTS, rng.choice([1, 1, 1, 2, 2, 3]))
        total = 0.0
        for p in items:
            qty = rng.choice([1, 1, 1, 2])
            c.execute('INSERT INTO order_items VALUES (?,?,?,?)', (oid, p[0], qty, p[3]))
            total += qty * p[3]
        total = round(total + (0 if total >= 150 else 8.90), 2)          # shipping fee below $150
        method = rng.choice(['card', 'card', 'bank transfer', 'bank transfer', 'e-wallet'])
        paid = placed + timedelta(minutes=rng.randint(1, 20))
        c.execute('INSERT INTO payments VALUES (?,?,?,?,?,?)', ('pay_%06d' % (n * 2), oid, method, total, 'captured', ts(paid)))
        if rng.random() < 0.03:                                           # a duplicate charge
            c.execute('INSERT INTO payments VALUES (?,?,?,?,?,?)', ('pay_%06d' % (n * 2 + 1), oid, method, total, 'captured',
                                                                     ts(paid + timedelta(seconds=rng.randint(20, 90)))))
        courier = rng.choice(COURIERS)
        shipped = placed + timedelta(hours=rng.randint(6, 60))
        promised = shipped + timedelta(days=rng.choice([2, 3, 3, 5]))
        city = cust[4]
        events = [(ts(shipped), 'Acme warehouse, Central', 'Picked up by courier')]
        fate = rng.random()
        delivered = None
        if shipped > now:
            status = 'processing'
            events = []
        else:
            hub_at = shipped + timedelta(hours=rng.randint(4, 30))
            events.append((ts(hub_at), rng.choice(HUBS), 'Arrived at hub'))
            if fate < 0.07:                                               # stuck: address problem
                events.append((ts(hub_at + timedelta(hours=8)), events[-1][1], 'Held: delivery address could not be verified'))
                status = 'delayed'
            elif fate < 0.11:                                             # failed delivery attempt
                t = hub_at + timedelta(days=1)
                events.append((ts(t), city, 'Out for delivery'))
                events.append((ts(t + timedelta(hours=6)), city, 'Delivery failed: recipient not available'))
                status = 'delayed'
            else:
                t = hub_at + timedelta(days=rng.choice([0, 1, 1, 2, 4]))
                if t > now:
                    status = 'shipped'
                    events.append((ts(min(t, now - timedelta(hours=2))), city, 'In transit to delivery area'))
                else:
                    events.append((ts(t), city, 'Out for delivery'))
                    delivered = t + timedelta(hours=rng.randint(2, 7))
                    events.append((ts(delivered), city, 'Delivered'))
                    status = 'delivered'
        c.execute('INSERT INTO orders VALUES (?,?,?,?,?,?,?)', (oid, cust[0], ts(placed), status, total, city,
                                                                ts(delivered) if delivered else None))
        if status != 'processing':
            c.execute('INSERT INTO shipments VALUES (?,?,?,?,?)', (oid, courier, '%s%09d' % (courier[:2].upper(), rng.randint(0, 999999999)),
                                                                   ts(shipped), ts(promised)))
            c.executemany('INSERT INTO tracking_events VALUES (?,?,?,?)', [(oid, a, l, e) for a, l, e in events])
        if status == 'delivered' and rng.random() < 0.05:
            c.execute('INSERT INTO refunds VALUES (?,?,?,?,?,?,?)', ('ref_%05d' % n, oid, round(total * rng.choice([0.3, 1.0]), 2),
                                                                     rng.choice(['damaged on arrival', 'wrong item', 'changed mind']),
                                                                     'completed', ts(delivered + timedelta(days=2)), 'agent'))
    _scenarios(c)
    con.commit()
    counts = {t: c.execute('SELECT COUNT(*) FROM %s' % t).fetchone()[0] for t in
              ('customers', 'orders', 'order_items', 'payments', 'shipments', 'tracking_events', 'refunds')}
    con.close()
    return counts


def _scenarios(c):
    """Fixed cases the examples and tickets refer to, so their answers can be checked."""
    # Alice: blender arrived cracked AND was charged twice
    c.execute("INSERT OR REPLACE INTO customers VALUES ('C-1182','Alice Smith','alice.smith@example.com','555-012-418 2290','Eastside','2025-03-14 10:02','gold')")
    c.execute("INSERT OR REPLACE INTO orders VALUES ('ord_20931','C-1182','2026-10-24 21:15','delivered',289.00,'Eastside','2026-10-27 14:40')")
    c.execute("DELETE FROM order_items WHERE order_id='ord_20931'")
    c.execute("INSERT INTO order_items VALUES ('ord_20931','P-101',1,289.00)")
    c.execute("DELETE FROM payments WHERE order_id='ord_20931'")
    c.executemany("INSERT INTO payments VALUES (?,?,?,?,?,?)", [('pay_920931','ord_20931','card',289.00,'captured','2026-10-24 21:16'),
                                                                 ('pay_920932','ord_20931','card',289.00,'captured','2026-10-24 21:17')])
    c.execute("INSERT OR REPLACE INTO shipments VALUES ('ord_20931','QuickParcel','JT004471920','2026-10-25 11:00','2026-10-28 18:00')")
    c.execute("DELETE FROM tracking_events WHERE order_id='ord_20931'")
    c.executemany("INSERT INTO tracking_events VALUES ('ord_20931',?,?,?)", [
        ('2026-10-25 11:00', 'Acme warehouse, Central', 'Picked up by courier'), ('2026-10-26 08:30', 'Eastside hub', 'Arrived at hub'),
        ('2026-10-27 09:10', 'Eastside', 'Out for delivery'), ('2026-10-27 14:40', 'Eastside', 'Delivered')])
    # Diana: air purifier delivered damaged three days ago (refund allowed by policy 2.2, but above $500)
    c.execute("INSERT OR REPLACE INTO customers VALUES ('C-1240','Diana Cole','diana.cole@example.com','555-013-552 0187','Northside','2025-07-09 11:45','standard')")
    c.execute("INSERT OR REPLACE INTO orders VALUES ('ord_21500','C-1240','2026-10-25 10:20','delivered',899.00,'Northside','2026-10-29 15:05')")
    c.execute("DELETE FROM order_items WHERE order_id='ord_21500'")
    c.execute("INSERT INTO order_items VALUES ('ord_21500','P-502',1,899.00)")
    c.execute("DELETE FROM payments WHERE order_id='ord_21500'")
    c.execute("INSERT INTO payments VALUES ('pay_921500','ord_21500','card',899.00,'captured','2026-10-25 10:22')")
    c.execute("INSERT OR REPLACE INTO shipments VALUES ('ord_21500','ParcelOne','NI778104422','2026-10-26 09:00','2026-10-29 18:00')")
    c.execute("DELETE FROM tracking_events WHERE order_id='ord_21500'")
    c.executemany("INSERT INTO tracking_events VALUES ('ord_21500',?,?,?)", [
        ('2026-10-26 09:00', 'Acme warehouse, Central', 'Picked up by courier'), ('2026-10-27 07:30', 'Central hub', 'Arrived at hub'),
        ('2026-10-29 10:15', 'Northside', 'Out for delivery'), ('2026-10-29 15:05', 'Northside', 'Delivered')])
    # Ryan: monitor stuck at the hub, address could not be verified
    c.execute("INSERT OR REPLACE INTO customers VALUES ('C-1219','Ryan Clark','ryan.clark7@example.com','555-016-733 5104','Hillside','2024-11-02 15:20','standard')")
    c.execute("INSERT OR REPLACE INTO orders VALUES ('ord_21044','C-1219','2026-10-22 13:05','delayed',1299.00,'Hillside',NULL)")
    c.execute("DELETE FROM order_items WHERE order_id='ord_21044'")
    c.execute("INSERT INTO order_items VALUES ('ord_21044','P-401',1,1299.00)")
    c.execute("DELETE FROM payments WHERE order_id='ord_21044'")
    c.execute("INSERT INTO payments VALUES ('pay_921044','ord_21044','bank transfer',1299.00,'captured','2026-10-22 13:09')")
    c.execute("INSERT OR REPLACE INTO shipments VALUES ('ord_21044','FastShip','PO118200417','2026-10-23 10:00','2026-10-26 18:00')")
    c.execute("DELETE FROM tracking_events WHERE order_id='ord_21044'")
    c.executemany("INSERT INTO tracking_events VALUES ('ord_21044',?,?,?)", [
        ('2026-10-23 10:00', 'Acme warehouse, Central', 'Picked up by courier'), ('2026-10-24 07:45', 'Lakeside hub', 'Arrived at hub'),
        ('2026-10-24 16:20', 'Lakeside hub', 'Held: delivery address could not be verified')])


if __name__ == '__main__':
    print(build())
