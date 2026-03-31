import os
import socket
import ssl
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv


# ---------------------------
# 0. Load environment
# ---------------------------
print("\n=== LOADING ENV ===")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    print("👉 Ensure .env exists in current directory")
    exit()

print("✅ DATABASE_URL loaded")
print("Preview:", DATABASE_URL.split("@")[-1])  # hide password


# ---------------------------
# 1. Parse URL
# ---------------------------
print("\n=== PARSING URL ===")
parsed = urlparse(DATABASE_URL)

host = parsed.hostname
port = parsed.port or 5432
user = parsed.username
password = parsed.password
db = parsed.path.lstrip("/")

print(f"Host: {host}")
print(f"Port: {port}")
print(f"User: {user}")
print(f"Database: {db}")
print(f"Password length: {len(password) if password else 0}")

if not all([host, user, password, db]):
    print("❌ Invalid DATABASE_URL format")
    exit()


# ---------------------------
# 2. DNS Resolution
# ---------------------------
print("\n=== DNS RESOLUTION ===")
try:
    ip = socket.gethostbyname(host)
    print(f"✅ Resolved to {ip}")
except Exception as e:
    print(f"❌ DNS failed: {e}")
    exit()


# ---------------------------
# 3. TCP Connection
# ---------------------------
print("\n=== TCP CONNECTION ===")
try:
    sock = socket.create_connection((host, port), timeout=5)
    print("✅ TCP connection successful")
    sock.close()
except Exception as e:
    print(f"❌ TCP failed: {e}")
    exit()


# ---------------------------
# 4. SSL Handshake
# ---------------------------
print("\n=== SSL HANDSHAKE ===")
try:
    context = ssl.create_default_context()
    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host):
            print("✅ SSL handshake successful")
except Exception as e:
    print(f"❌ SSL failed: {e}")
    exit()


# ---------------------------
# 5. Database Authentication
# ---------------------------
print("\n=== DATABASE AUTH TEST ===")

# Remove risky params (like channel_binding)
clean_url = DATABASE_URL.split("&channel_binding")[0]

try:
    conn = psycopg2.connect(clean_url)
    print("✅ AUTH SUCCESS — connection established")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("PostgreSQL Version:", version[0])

    cur.close()
    conn.close()

except Exception as e:
    print("❌ AUTH FAILED")
    print(type(e).__name__, ":", e)