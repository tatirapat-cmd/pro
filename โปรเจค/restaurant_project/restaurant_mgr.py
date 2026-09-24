# restaurant_mgr.py
# ระบบจัดการฐานข้อมูลจำลอง (Menu, Tables, Orders, Bill, Sales Report)

menu_db = []
   
tables_db = [
    {"table_id": 1, "status": "ว่าง", "reservation": None},
    {"table_id": 2, "status": "ว่าง", "reservation": None},
    {"table_id": 3, "status": "ว่าง", "reservation": None},
    {"table_id": 4, "status": "ว่าง", "reservation": None}
]

orders_db = []
completed_sales_db = []
order_counter = 1

def get_categories():
    return [
        "อาหารเรียกน้ำย่อย / ของทานเล่น (Appetizers / Starters)",
        "อาหารจานหลัก (Main Courses)",
        "อาหารจานเดียว / ข้าวและเส้น (Single Dishes / Rice & Noodles)",
        "อาหารประเภทกับข้าว (Shared Dishes)",
        "ของหวาน (Desserts)",
        "เครื่องดื่ม (Beverages)"
    ]

def get_all_menu():
    return menu_db

def get_menu_by_id(menu_id):
    return next((m for m in menu_db if m['id'] == menu_id), None)

def add_menu_item(user, name, category, price, image_url=""):
    if not user or user.get('role') != 'admin':
        return False, "สิทธิ์ไม่ถูกต้อง (ต้องเป็น Admin เท่านั้น)"
    
    new_id = max([m['id'] for m in menu_db], default=0) + 1
    new_item = {
        "id": new_id,
        "name": name,
        "category": category,
        "price": float(price),
        "image_url": image_url,
        "is_available": True
    }
    menu_db.append(new_item)
    return True, f"เพิ่มเมนู '{name}' เรียบร้อยแล้ว"

# --- ✏️ ระบบแก้ไขเมนูอาหาร ---
def update_menu_item(user, menu_id, name, category, price, image_url, is_available=True):
    if not user or user.get('role') != 'admin':
        return False, "เฉพาะผู้ดูแลระบบ (Admin) เท่านั้นที่สามารถแก้ไขเมนูได้"
    
    for item in menu_db:
        if item['id'] == menu_id:
            item['name'] = name
            item['category'] = category
            item['price'] = float(price)
            item['image_url'] = image_url
            item['is_available'] = is_available
            return True, f"แก้ไขข้อมูลเมนู '{name}' เรียบร้อยแล้ว"
            
    return False, "ไม่พบเมนูที่ต้องการแก้ไข"

# --- 🗑️ ระบบลบเมนูอาหาร ---
def delete_menu_item(user, menu_id):
    global menu_db
    if not user or user.get('role') != 'admin':
        return False, "เฉพาะผู้ดูแลระบบ (Admin) เท่านั้นที่สามารถลบเมนูได้"
    
    initial_len = len(menu_db)
    menu_db = [m for m in menu_db if m['id'] != menu_id]
    
    if len(menu_db) < initial_len:
        return True, "ลบเมนูอาหารเรียบร้อยแล้ว"
    return False, "ไม่พบเมนูที่ต้องการลบ"

def update_menu_status(menu_id, is_available):
    for item in menu_db:
        if item['id'] == menu_id:
            item['is_available'] = is_available
            return True, "อัปเดตสถานะเมนูสำเร็จ"
    return False, "ไม่พบรายการเมนู"

# --- 🪑 ระบบจัดการเพิ่ม/ลบโต๊ะ ---
def get_all_tables():
    return tables_db

def add_table_by_app(table_id=None):
    global tables_db
    if table_id is None or table_id == "":
        table_id = max([t['table_id'] for t in tables_db], default=0) + 1
    else:
        table_id = int(table_id)
        if any(t['table_id'] == table_id for t in tables_db):
            return False, f"มีโต๊ะหมายเลข {table_id} ในระบบอยู่แล้ว"

    tables_db.append({"table_id": table_id, "status": "ว่าง", "reservation": None})
    return True, f"เพิ่มโต๊ะหมายเลข {table_id} เรียบร้อยแล้ว"

def delete_table(table_id):
    global tables_db
    table = next((t for t in tables_db if t['table_id'] == table_id), None)
    if not table:
        return False, "ไม่พบโต๊ะดังกล่าว"
    if table['status'] != "ว่าง":
        return False, "ไม่สามารถลบโต๊ะที่มีลูกค้าหรือติดจองอยู่ได้"

    tables_db = [t for t in tables_db if t['table_id'] != table_id]
    return True, f"ลบโต๊ะหมายเลข {table_id} เรียบร้อยแล้ว"

# --- 📅 ระบบจองโต๊ะอาหาร ---
def reserve_table(table_id, customer_name, phone, reserve_time):
    table = next((t for t in tables_db if t['table_id'] == table_id), None)
    if not table:
        return False, "ไม่พบโต๊ะ"
    if table['status'] != "ว่าง":
        return False, "โต๊ะนี้ไม่ว่างสำหรับจอง"

    table['status'] = "จองแล้ว"
    table['reservation'] = {
        "customer_name": customer_name,
        "phone": phone,
        "reserve_time": reserve_time
    }
    return True, f"จองโต๊ะ {table_id} สำเร็จ (คุณ {customer_name})"

def cancel_reservation(table_id):
    table = next((t for t in tables_db if t['table_id'] == table_id), None)
    if not table:
        return False, "ไม่พบโต๊ะ"
    if table['status'] != "จองแล้ว":
        return False, "โต๊ะนี้ไม่ได้อยู่ในสถานะจอง"

    table['status'] = "ว่าง"
    table['reservation'] = None
    return True, f"ยกเลิกการจองโต๊ะ {table_id} เรียบร้อยแล้ว"

def occupy_reserved_table(table_id):
    table = next((t for t in tables_db if t['table_id'] == table_id), None)
    if not table:
        return False, "ไม่พบโต๊ะ"
    table['status'] = "มีลูกค้า"
    table['reservation'] = None
    return True, f"เปิดโต๊ะ {table_id} สำหรับลูกค้าเรียบร้อยแล้ว"

# --- 🛒 ระบบออเดอร์และการเงิน ---
def add_order(table_id, menu_id, quantity):
    global order_counter
    menu_item = next((m for m in menu_db if m['id'] == menu_id and m['is_available']), None)
    if not menu_item:
        return False, "เมนูนี้ไม่พร้อมให้บริการ"

    order = {
        "order_id": order_counter,
        "table_id": table_id,
        "menu_id": menu_id,
        "menu_name": menu_item['name'],
        "price": menu_item['price'],
        "quantity": int(quantity),
        "status": "รอดำเนินการ"
    }
    orders_db.append(order)
    order_counter += 1

    for t in tables_db:
        if t['table_id'] == table_id:
            t['status'] = "มีลูกค้า"
            
    return True, f"สั่งอาหาร '{menu_item['name']}' จำนวน {quantity} เรียบร้อย"

def get_kitchen_orders():
    return [o for o in orders_db if o['status'] in ["รอดำเนินการ", "กำลังเตรียม"]]

def update_order_status(order_id, new_status):
    for o in orders_db:
        if o['order_id'] == order_id:
            o['status'] = new_status
            return True, f"อัปเดตสถานะออเดอร์ #{order_id} เป็น '{new_status}' แล้ว"
    return False, "ไม่พบออเดอร์"

def calculate_bill(table_id):
    table_orders = [o for o in orders_db if o['table_id'] == table_id and o['status'] != "ชำระเงินแล้ว"]
    if not table_orders:
        return {"items": [], "raw_total": 0.0}
    
    raw_total = sum(o['price'] * o['quantity'] for o in table_orders)
    return {
        "items": table_orders,
        "raw_total": raw_total
    }

def process_checkout(user, table_id, discount_pct=0.0):
    if not user or user.get('role') not in ['admin', 'staff']:
        return False, "ไม่มีสิทธิ์ทำรายการ", 0.0

    bill = calculate_bill(table_id)
    if not bill['items']:
        return False, "ไม่พบรายการอาหารที่ต้องชำระในโต๊ะนี้", 0.0

    raw_total = bill['raw_total']
    service_charge = raw_total * 0.10
    subtotal = raw_total + service_charge
    
    discount_amount = subtotal * (discount_pct / 100.0)
    amount_after_discount = subtotal - discount_amount
    vat = amount_after_discount * 0.07
    net_total = amount_after_discount + vat

    for o in bill['items']:
        o['status'] = "ชำระเงินแล้ว"
        completed_sales_db.append(o)

    for t in tables_db:
        if t['table_id'] == table_id:
            t['status'] = "ว่าง"
            t['reservation'] = None

    return True, f"เช็คบิลโต๊ะ {table_id} เรียบร้อย ยอดชำระสุทธิ: {net_total:.2f} บาท", net_total

def generate_sales_report():
    total_revenue = 0.0
    item_counts = {}
    category_revenue = {} # เพิ่มการเก็บยอดขายตามหมวดหมู่

    for item in completed_sales_db:
        revenue = item['price'] * item['quantity']
        total_revenue += revenue
        
        # นับจำนวนเมนูขายดี
        name = item['menu_name']
        item_counts[name] = item_counts.get(name, 0) + item['quantity']

        # คำนวณรายได้ตามหมวดหมู่
        # (ดึงหมวดหมู่จาก menu_db ถ้าหาไม่พบให้เป็น 'อื่นๆ')
        menu_info = next((m for m in menu_db if m['id'] == item.get('menu_id')), None)
        category = menu_info['category'] if menu_info else "อื่นๆ"
        category_revenue[category] = category_revenue.get(category, 0.0) + revenue

    sorted_bestsellers = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_revenue": total_revenue,
        "total_orders": len(completed_sales_db),
        "best_sellers": sorted_bestsellers,
        "category_revenue": category_revenue # ส่งข้อมูลหมวดหมู่กลับไปด้วย
    }