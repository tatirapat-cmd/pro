# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from auth import login_user, register_user, check_permission
from restaurant_mgr import (
    get_all_menu, get_menu_by_id, add_menu_item, update_menu_item, delete_menu_item,
    get_all_tables, add_table_by_app, delete_table,
    reserve_table, cancel_reservation, occupy_reserved_table,
    add_order, get_kitchen_orders, update_order_status,
    calculate_bill, process_checkout, generate_sales_report, get_categories
)

app = Flask(__name__)
app.secret_key = 'kku_restaurant_secret_key_tcas69'

@app.route('/')
def index():
    menu = get_all_menu()
    return render_template('dashboard.html', menu=menu)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = login_user(request.form['username'], request.form['password'])
        if user:
            session['user'] = user
            flash("เข้าสู่ระบบสำเร็จ!", "success")
            return redirect(url_for('index'))
        flash("Username หรือ Password ไม่ถูกต้อง", "error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'customer')
        
        success, msg = register_user(username, password, role)
        if success:
            flash(f"{msg} กรุณาเข้าสู่ระบบ", "success")
            return redirect(url_for('login'))
        else:
            flash(msg, "error")
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("ออกจากระบบเรียบร้อยแล้ว", "success")
    return redirect(url_for('index'))

@app.route('/add_menu', methods=['GET', 'POST'])
def add_menu():
    if not session.get('user') or session['user']['role'] != 'admin':
        flash("เฉพาะผู้ดูแลระบบ (Admin) เท่านั้นที่สามารถเพิ่มเมนูได้", "error")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        try:
            price = float(request.form['price'])
            image_url = request.form.get('image_url', '').strip()
            
            succ, msg = add_menu_item(session['user'], name, category, price, image_url)
            flash(msg, "success" if succ else "error")
            if succ:
                return redirect(url_for('index'))
        except ValueError:
            flash("กรุณากรอกราคาให้ถูกต้อง", "error")
            
    return render_template('add_menu.html')

# --- ✏️ Route แก้ไขเมนูอาหาร ---
@app.route('/edit_menu/<int:menu_id>', methods=['GET', 'POST'])
def edit_menu(menu_id):
    if not session.get('user') or session['user']['role'] != 'admin':
        flash("เฉพาะผู้ดูแลระบบ (Admin) เท่านั้นที่สามารถแก้ไขเมนูได้", "error")
        return redirect(url_for('index'))
        
    item = get_menu_by_id(menu_id)
    if not item:
        flash("ไม่พบเมนูอาหารที่ต้องการแก้ไข", "error")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        try:
            price = float(request.form['price'])
            image_url = request.form.get('image_url', '').strip()
            is_available = 'is_available' in request.form
            
            succ, msg = update_menu_item(session['user'], menu_id, name, category, price, image_url, is_available)
            flash(msg, "success" if succ else "error")
            if succ:
                return redirect(url_for('index'))
        except ValueError:
            flash("กรุณากรอกราคาให้ถูกต้อง", "error")
            
    categories = get_categories()
    return render_template('edit_menu.html', item=item, categories=categories)

# --- 🗑️ Route ลบเมนูอาหาร ---
@app.route('/delete_menu/<int:menu_id>', methods=['POST'])
def handle_delete_menu(menu_id):
    if not session.get('user') or session['user']['role'] != 'admin':
        flash("เฉพาะผู้ดูแลระบบ (Admin) เท่านั้นที่สามารถลบเมนูได้", "error")
        return redirect(url_for('index'))
        
    succ, msg = delete_menu_item(session['user'], menu_id)
    flash(msg, "success" if succ else "error")
    return redirect(url_for('index'))

# --- 🪑 Routes จัดการโต๊ะ ---
@app.route('/tables')
def tables():
    return render_template('tables.html', tables=get_all_tables(), menu=get_all_menu())

@app.route('/add_table', methods=['POST'])
def handle_add_table():
    if not session.get('user') or session['user']['role'] not in ['admin', 'staff']:
        flash("เฉพาะพนักงานหรือผู้ดูแลระบบเท่านั้นที่เพิ่มโต๊ะได้", "error")
        return redirect(url_for('tables'))
        
    custom_id = request.form.get('table_id', '').strip()
    t_id = int(custom_id) if custom_id else None
    succ, msg = add_table_by_app(t_id)
    flash(msg, "success" if succ else "error")
    return redirect(url_for('tables'))

@app.route('/delete_table/<int:table_id>', methods=['POST'])
def handle_delete_table(table_id):
    if not session.get('user') or session['user']['role'] != 'admin':
        flash("เฉพาะผู้ดูแลระบบ (Admin) เท่านั้นที่ลบโต๊ะได้", "error")
        return redirect(url_for('tables'))
        
    succ, msg = delete_table(table_id)
    flash(msg, "success" if succ else "error")
    return redirect(url_for('tables'))

# --- 📅 Routes จองโต๊ะ ---
@app.route('/reserve_table', methods=['POST'])
def handle_reserve_table():
    t_id = int(request.form['table_id'])
    c_name = request.form['customer_name']
    phone = request.form['phone']
    r_time = request.form['reserve_time']
    
    succ, msg = reserve_table(t_id, c_name, phone, r_time)
    flash(msg, "success" if succ else "error")
    return redirect(url_for('tables'))

@app.route('/cancel_reservation/<int:table_id>', methods=['POST'])
def handle_cancel_reservation(table_id):
    succ, msg = cancel_reservation(table_id)
    flash(msg, "success" if succ else "error")
    return redirect(url_for('tables'))

@app.route('/occupy_table/<int:table_id>', methods=['POST'])
def handle_occupy_table(table_id):
    succ, msg = occupy_reserved_table(table_id)
    flash(msg, "success" if succ else "error")
    return redirect(url_for('tables'))

@app.route('/add_order', methods=['POST'])
def handle_add_order():
    t_id = int(request.form['table_id'])
    m_id = int(request.form['menu_id'])
    qty = int(request.form['quantity'])
    
    succ, msg = add_order(t_id, m_id, qty)
    flash(msg, "success" if succ else "error")
    return redirect(url_for('tables'))

@app.route('/kitchen')
def kitchen():
    if not session.get('user') or session['user']['role'] not in ['admin', 'staff']:
        flash("ไม่มีสิทธิ์เข้าถึงหน้านี้", "error")
        return redirect(url_for('index'))
    return render_template('kitchen.html', orders=get_kitchen_orders())

@app.route('/update_kitchen', methods=['POST'])
def update_kitchen():
    order_id = int(request.form['order_id'])
    status = request.form['status']
    succ, msg = update_order_status(order_id, status)
    flash(msg, "success" if succ else "error")
    return redirect(url_for('kitchen'))

@app.route('/checkout/<int:table_id>')
def checkout_view(table_id):
    if not session.get('user') or session['user']['role'] not in ['admin', 'staff']:
        flash("เฉพาะ Staff หรือ Admin เท่านั้นที่สามารถเช็คบิลได้", "error")
        return redirect(url_for('tables'))
    
    bill = calculate_bill(table_id)
    raw_total = bill['raw_total']

    return render_template('checkout.html', table_id=table_id, bill=bill, raw_total=raw_total)

@app.route('/process_checkout', methods=['POST'])
def handle_process_checkout():
    if not session.get('user') or session['user']['role'] not in ['admin', 'staff']:
        flash("เฉพาะ Staff หรือ Admin เท่านั้นที่ทำรายการได้", "error")
        return redirect(url_for('tables'))
        
    table_id = int(request.form['table_id'])
    discount_raw = request.form.get('discount', '0').strip()
    try:
        discount = float(discount_raw) if discount_raw else 0.0
    except ValueError:
        discount = 0.0
    
    succ, msg, _ = process_checkout(session['user'], table_id, discount_pct=discount)
    flash(msg, "success" if succ else "error")
    return redirect(url_for('tables'))

@app.route('/report')
def report():
    if not session.get('user') or session['user']['role'] != 'admin':
        flash("เฉพาะ Admin เท่านั้นที่เข้าถึงหน้านี้ได้", "error")
        return redirect(url_for('index'))
    return render_template('report.html', report=generate_sales_report())

if __name__ == '__main__':
    print("🚀 เริ่มรันระบบร้านอาหารที่ http://127.0.0.1:5000")
    app.run(debug=True, port=5000)