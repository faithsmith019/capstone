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
            created_by TEXT,
            assigned_to TEXT,
            requestor_email TEXT,
            full_name TEXT,
            phone TEXT,
            date TEXT,
            building TEXT,
            apartment TEXT,
            location TEXT,
            worker_viewed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            request_id INTEGER,
            notification_type TEXT NOT NULL,
            message TEXT NOT NULL,
            read INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ensure any previously-created database gets the new columns
    cursor.execute("PRAGMA table_info(maintenance_requests)")
    existing = {row[1] for row in cursor.fetchall()}
    for col in ('full_name','phone','date','building','apartment','location','requestor_email','created_by','assigned_to','worker_viewed'):
        if col not in existing:
            cursor.execute(f"ALTER TABLE maintenance_requests ADD COLUMN {col} TEXT")

    cursor.execute("PRAGMA table_info(notifications)")
    existing_notif = {row[1] for row in cursor.fetchall()}
    if 'notification_type' not in existing_notif:
        cursor.execute("ALTER TABLE notifications ADD COLUMN notification_type TEXT DEFAULT 'status'")

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
    created_by: str,
    requestor_email: str = "",
    assigned_to: str = "",
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
            requestor_email, full_name, phone, date, building, apartment, location,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title, description, status, created_by, assigned_to,
        requestor_email, full_name, phone, date, building, apartment, location,
        created_at, updated_at
    ))

    conn.commit()
    conn.close()


def get_request_by_id(request_id: int):
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, status, created_by, assigned_to,
               requestor_email, full_name, phone, date, building, apartment, location,
               created_at, updated_at
        FROM maintenance_requests
        WHERE id = ?
    """, (request_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'status': row[3],
            'created_by': row[4],
            'assigned_to': row[5],
            'requestor_email': row[6],
            'full_name': row[7],
            'phone': row[8],
            'date': row[9],
            'building': row[10],
            'apartment': row[11],
            'location': row[12],
            'created_at': row[13],
            'updated_at': row[14],
        }
    return None


def add_notification(user_id: str, request_id: int, message: str, notification_type: str = "status"):
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notifications (user_id, request_id, notification_type, message)
        VALUES (?, ?, ?, ?)
    """, (user_id, request_id, notification_type, message))
    conn.commit()
    conn.close()


def get_notifications_for_user(user_id: str, unread_only: bool = True):
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if unread_only:
        cursor.execute("""
            SELECT id, user_id, request_id, notification_type, message, read, created_at
            FROM notifications
            WHERE user_id = ? AND read = 0
            ORDER BY created_at DESC
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT id, user_id, request_id, notification_type, message, read, created_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    notifications = []
    for r in rows:
        notifications.append({
            'id': r[0],
            'user_id': r[1],
            'request_id': r[2],
            'notification_type': r[3],
            'message': r[4],
            'read': r[5],
            'created_at': r[6],
        })
    return notifications


def mark_notifications_read(user_id: str):
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications
        SET read = 1
        WHERE user_id = ? AND read = 0
    """, (user_id,))
    conn.commit()
    conn.close()


def get_requests(all_status: bool = True):
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if all_status:
        cursor.execute("""
            SELECT id, title, description, status, created_by, assigned_to,
                   requestor_email, full_name, phone, date, building, apartment, location, worker_viewed
            FROM maintenance_requests
            ORDER BY created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT id, title, description, status, created_by, assigned_to,
                   requestor_email, full_name, phone, date, building, apartment, location, worker_viewed
            FROM maintenance_requests
            WHERE status = 'open'
            ORDER BY created_at DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    requests = []
    for row in rows:
        requests.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'status': row[3],
            'created_by': row[4],
            'assigned_to': row[5],
            'requestor_email': row[6],
            'full_name': row[7],
            'phone': row[8],
            'date': row[9],
            'building': row[10],
            'apartment': row[11],
            'location': row[12],
            'worker_viewed': row[13],
        })
    return requests


def mark_request_seen(request_id: int):
    """Mark a request as viewed by a worker and send notification to requestor."""
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get request details first
    cursor.execute("""
        SELECT created_by, requestor_email, worker_viewed
        FROM maintenance_requests
        WHERE id = ?
    """, (request_id,))
    row = cursor.fetchone()
    
    if row and row[2] == 0:  # Only if not already marked as viewed
        # Mark as viewed
        cursor.execute("""
            UPDATE maintenance_requests
            SET worker_viewed = 1
            WHERE id = ?
        """, (request_id,))
        conn.commit()
        
        # Send notification to requestor
        requestor_id = row[0] or row[1]
        if requestor_id:
            cursor.execute("""
                INSERT INTO notifications (user_id, request_id, notification_type, message)
                VALUES (?, ?, ?, ?)
            """, (requestor_id, request_id, "seen", f"Your maintenance request #{request_id} has been reviewed by a worker."))
            conn.commit()
    
    conn.close()


def assign_request_to_worker(request_id: int, worker_id: str):
    """Assign a request to a worker and send notification to requestor."""
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get request details
    cursor.execute("""
        SELECT created_by, requestor_email
        FROM maintenance_requests
        WHERE id = ?
    """, (request_id,))
    row = cursor.fetchone()
    
    if row:
        # Update assignment
        cursor.execute("""
            UPDATE maintenance_requests
            SET assigned_to = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (worker_id, request_id))
        conn.commit()
        
        # Send notification to requestor
        requestor_id = row[0] or row[1]
        if requestor_id:
            cursor.execute("""
                INSERT INTO notifications (user_id, request_id, notification_type, message)
                VALUES (?, ?, ?, ?)
            """, (requestor_id, request_id, "assigned", f"Your maintenance request #{request_id} has been assigned to a worker."))
            conn.commit()
    
    conn.close()


