# auth.py
# ระบบจัดการการเข้าสู่ระบบ สมัครสมาชิก และสิทธิ์ผู้ใช้งาน

users_db = {
    "TBO": {"password": "123456", "role": "admin"},
    "staff": {"password": "staffpassword", "role": "staff"}
}

def login_user(username, password):
    user = users_db.get(username)
    if user and user['password'] == password:
        return {"username": username, "role": user['role']}
    return None

def register_user(username, password, role="customer"):
    if username in users_db:
        return False, "Username นี้มีผู้ใช้งานแล้ว"
    if role == "admin":
        return False, "ไม่สามารถสมัครเป็น Admin โดยตรงได้"
    
    users_db[username] = {"password": password, "role": role}
    return True, "สมัครสมาชิกสำเร็จ"

def check_permission(user, allowed_roles):
    if not user:
        return False
    return user.get('role') in allowed_roles