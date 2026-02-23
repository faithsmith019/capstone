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
    
    # Create maintenance_requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_by INTEGER,
            assigned_to INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
    """)
    
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

def add_maintenance_request(title: str, description: str, created_by: int, assigned_to: str = "none", status: str = "open", created_at: str = "", updated_at: str = "", fullname: str = "", phone: str = "", date: str = "", building: str = "", apartment: str = "", location: str = ""):
    """Add a new maintenance request to the database."""
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO maintenance_requests (title, description, created_by, assigned_to, status, created_at, updated_at, fullname, phone, date, building, apartment, location) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, description, created_by, assigned_to, status, created_at, updated_at, fullname, phone, date, building, apartment, location))
    
    conn.commit()
    conn.close()

