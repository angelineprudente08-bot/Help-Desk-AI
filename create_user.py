"""Create a technician or administrator account. (Requesters use the Register page.)"""
from getpass import getpass
from werkzeug.security import generate_password_hash
from db import get_db

name = input("Full name: ").strip()
email = input("Email: ").strip().lower()
role = input("Role (technician / administrator): ").strip().lower()
if role not in ("technician", "administrator"):
    raise SystemExit("Role must be technician or administrator.")
password = getpass("Password (hidden while you type): ")
if len(password) < 6:
    raise SystemExit("Use at least 6 characters.")

conn = get_db()
conn.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
             (name, email, generate_password_hash(password), role))
conn.commit()
conn.close()
print(f"Created {role} account for {email}")