"""Builds the two documents of the Acme support project from store.db:

    invoice_ord_20931.pdf     the invoice of the blender order charged twice (ticket T-1001)
    slip_ord_21044.png        the courier's delivery exception notice for the held parcel (ticket T-1002)

    python data/build_documents.py      (needs reportlab and pillow)
"""
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
db = sqlite3.connect(HERE / "store.db")
q = lambda sql, *a: db.execute(sql, a).fetchall()


def invoice(order_id: str) -> None:
    (o,) = q("SELECT o.placed_at, o.total, c.name, c.email, c.city FROM orders o "
             "JOIN customers c USING (customer_id) WHERE order_id = ?", order_id)
    items = q("SELECT p.name, i.qty, i.unit_price FROM order_items i JOIN products p USING (product_id) "
              "WHERE order_id = ?", order_id)
    pays = q("SELECT payment_id, method, amount, status, paid_at FROM payments WHERE order_id = ? "
             "ORDER BY paid_at", order_id)
    c = canvas.Canvas(str(HERE / f"invoice_{order_id}.pdf"), pagesize=A4)
    c.setTitle(f"Acme Electronics invoice {order_id}")
    y = 800
    def line(text, size=10, bold=False, x=50, step=16):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(x, y, text)
        y -= step
    line("Acme Electronics", 18, True, step=22)
    line("Online store  |  support@acme.example", 9, step=30)
    line(f"INVOICE  {order_id.upper().replace('ORD_', 'INV-')}", 14, True, step=20)
    line(f"Order: {order_id}    Placed: {o[0]}", step=14)
    line(f"Bill to: {o[2]}, {o[4]}  ({o[3]})", step=28)
    def row(cells, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 10)
        for x, cell in zip((50, 320, 380, 480), cells):
            c.drawString(x, y, cell)
        y -= 16
    row(("Item", "Qty", "Unit price", "Amount"), True)
    for name, qty, price in items:
        row((name, str(qty), f"USD {price:.2f}", f"USD {qty * price:.2f}"))
    y -= 8
    line(f"Order total: USD {o[1]:.2f}", 11, True, step=30)
    line("Payments received", 11, True)
    for pid, method, amount, status, at in pays:
        line(f"{at}   {pid}   {method:<6} {status:<9} USD {amount:.2f}", 10)
    line(f"Total charged: USD {sum(p[2] for p in pays):.2f}", 11, True, step=30)
    line("Returns and refunds follow the Acme refund policy v4.2.", 9)
    c.save()


def slip(order_id: str) -> None:
    (s,) = q("SELECT s.courier, s.tracking_no, c.name, o.ship_city FROM shipments s JOIN orders o USING (order_id) "
             "JOIN customers c USING (customer_id) WHERE order_id = ?", order_id)
    at, where, event = q("SELECT at, location, event FROM tracking_events WHERE order_id = ? "
                         "ORDER BY at DESC LIMIT 1", order_id)[0]
    img = Image.new("RGB", (900, 560), (250, 248, 240))
    d = ImageDraw.Draw(img)
    try:
        big, body = ImageFont.truetype("arialbd.ttf", 34), ImageFont.truetype("arial.ttf", 24)
    except OSError:
        big = body = ImageFont.load_default()
    d.rectangle([20, 20, 880, 540], outline=(40, 40, 40), width=3)
    d.rectangle([20, 20, 880, 90], fill=(200, 40, 40))
    d.text((40, 35), f"{s[0]}  DELIVERY EXCEPTION NOTICE", font=big, fill="white")
    rows = [("Tracking number", s[1]), ("Reference", order_id), ("Consignee", f"{s[2]}, {s[3]}"),
            ("Status", event.split(":")[0]), ("Reason", event.split(":", 1)[1].strip() if ":" in event else event),
            ("Held at", f"{where}, since {at}"), ("Action", "Confirm the address with the sender within 7 days")]
    for i, (k, v) in enumerate(rows):
        d.text((50, 120 + i * 56), k, font=body, fill=(90, 90, 90))
        d.text((300, 120 + i * 56), v, font=body, fill=(20, 20, 20))
    img.save(HERE / f"slip_{order_id}.png")


invoice("ord_20931")
slip("ord_21044")
print("built invoice_ord_20931.pdf and slip_ord_21044.png")
