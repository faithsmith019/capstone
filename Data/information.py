# the database for the web app
import sqlite3
from pathlib import Path    

def init_db():
    """Initialize the SQLite database and create necessary tables."""
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # Create maintenance_requests table with additional fields for requestor details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_by INTEGER,
            assigned_to INTEGER,
            full_name TEXT,
            phone TEXT,
            date TEXT,
            building TEXT,
            apartment TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
    """)
    # ensure any previously-created database gets the new columns
    cursor.execute("PRAGMA table_info(maintenance_requests)")
    existing = {row[1] for row in cursor.fetchall()}
    for col in ('full_name','phone','date','building','apartment','location'):
        if col not in existing:
            cursor.execute(f"ALTER TABLE maintenance_requests ADD COLUMN {col} TEXT")
    
    conn.commit()
    conn.close()

def add_user(username: str, name: str, role: str, password: str):
    """Add a new user to the database."""
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users (username, name, role, password) 
        VALUES (?, ?, ?, ?)
    """, (username, name, role, password))
    
    conn.commit()
    conn.close()

def add_maintenance_request(
    title: str,
    description: str,
    created_by: int,
    assigned_to: str = "none",
    status: str = "open",
    created_at: str = "",
    updated_at: str = "",
    full_name: str = "",
    phone: str = "",
    date: str = "",
    building: str = "",
    apartment: str = "",
    location: str = ""
):
    """Add a new maintenance request to the database."""
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO maintenance_requests (
            title, description, status, created_by, assigned_to,
            full_name, phone, date, building, apartment, location,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title, description, status, created_by, assigned_to,
        full_name, phone, date, building, apartment, location,
        created_at, updated_at
    ))
    
    conn.commit()
    conn.close()

