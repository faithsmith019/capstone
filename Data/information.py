# the database for the web app
import sqlite3
from pathlib import Path    
import os

# Set email credentials
os.environ['EMAIL_SENDER'] = 'falconfacilities2026@gmail.com'
os.environ['EMAIL_PASSWORD'] = 'vefyxrqrpzgmxcrr'

# Import email service from the Controller package so status-change emails can be sent
import sys
sys.path.append(str(Path(__file__).parents[1] / "Controller"))
from emailService import send_status_notification_email    

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
            priority TEXT DEFAULT 'normal',
            hold_reason TEXT,
            notes TEXT,
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
    for col in ('full_name','phone','date','building','apartment','location','requestor_email','created_by','assigned_to','worker_viewed','priority','hold_reason','notes'):
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
    """Retrieve a single maintenance request by its ID.

    Inputs:
        request_id: the ID of the request to fetch.
    Returns:
        A dict of request fields or None if not found.
    """
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, status, created_by, assigned_to,
               requestor_email, full_name, phone, date, building, apartment, location,
               priority, hold_reason, notes, created_at, updated_at
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
            'priority': row[13],
            'hold_reason': row[14],
            'notes': row[15],
            'created_at': row[16],
            'updated_at': row[17],
        }
    return None


def add_notification(user_id: str, request_id: int, message: str, notification_type: str = "status"):
    """Create a notification for a user.

    Inputs:
        user_id: the recipient user identifier.
        request_id: related maintenance request ID.
        message: notification text.
        notification_type: category of notification.
    """
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
    """Fetch notifications for a user.

    Inputs:
        user_id: the user whose notifications are fetched.
        unread_only: whether to return only unread notifications.
    Returns:
        List of notification dictionaries.
    """
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
    """Mark all unread notifications for a user as read."""
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
    """Load maintenance requests from the database.

    Inputs:
        all_status: if True, return requests of all statuses; otherwise return only open requests.
    Returns:
        List of request dictionaries.
    """
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if all_status:
        cursor.execute("""
            SELECT id, title, description, status, created_by, assigned_to,
                   requestor_email, full_name, phone, date, building, apartment, location, worker_viewed, priority, hold_reason, notes
            FROM maintenance_requests
            ORDER BY created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT id, title, description, status, created_by, assigned_to,
                   requestor_email, full_name, phone, date, building, apartment, location, worker_viewed, priority, hold_reason, notes
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
            'priority': row[14],
            'hold_reason': row[15],
            'notes': row[16],
        })
    return requests


def update_request_details(request_id: int, status: str = None, priority: str = None, hold_reason: str = None, notes: str = None):
    """Update fields on an existing maintenance request.

    Inputs:
        request_id: ID of the request to update.
        status: new status value, if provided.
        priority: new priority, if provided.
        hold_reason: hold reason text, if provided.
        notes: technician notes, if provided.
    """
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Build the update query dynamically
    update_fields = []
    values = []
    if status is not None:
        update_fields.append("status = ?")
        values.append(status)
    if priority is not None:
        update_fields.append("priority = ?")
        values.append(priority)
    if hold_reason is not None:
        update_fields.append("hold_reason = ?")
        values.append(hold_reason)
    if notes is not None:
        update_fields.append("notes = ?")
        values.append(notes)
    
    if update_fields:
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE maintenance_requests SET {', '.join(update_fields)} WHERE id = ?"
        values.append(request_id)
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()


def mark_request_seen(request_id: int):
    """Mark a request as seen by a worker and update its queue status."""
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get request details first
    cursor.execute("""
        SELECT created_by, requestor_email, worker_viewed, status, full_name
        FROM maintenance_requests
        WHERE id = ?
    """, (request_id,))
    row = cursor.fetchone()
    
    if row and row[2] == 0:  # Only if not already marked as viewed
        # Mark as viewed and change status from approved to queued
        new_status = 'queued' if row[3] == 'approved' else row[3]
        cursor.execute("""
            UPDATE maintenance_requests
            SET worker_viewed = 1, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_status, request_id))
        conn.commit()
        
        # Send notification to requestor
        requestor_id = row[0] or row[1]
        if requestor_id:
            message = f"Your maintenance request #{request_id} is now queued for assignment."
            cursor.execute("""
                INSERT INTO notifications (user_id, request_id, notification_type, message)
                VALUES (?, ?, ?, ?)
            """, (requestor_id, request_id, "seen", message))
            conn.commit()
            
            # Send email notification if requestor_email is available
            requestor_email = row[1]
            if requestor_email:
                send_status_notification_email(requestor_email, request_id, new_status, message, row[4] or "")
    
    conn.close()


def assign_request_to_worker(request_id: int, worker_id: str):
    """Assign a maintenance request to a worker and notify the requestor."""
    db_path = Path(__file__).parent / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get request details
    cursor.execute("""
        SELECT created_by, requestor_email, status, full_name
        FROM maintenance_requests
        WHERE id = ?
    """, (request_id,))
    row = cursor.fetchone()
    
    if row:
        # Update assignment and change status to in_progress
        cursor.execute("""
            UPDATE maintenance_requests
            SET assigned_to = ?, status = 'in_progress', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (worker_id, request_id))
        conn.commit()
        
        # Send notification to requestor
        requestor_id = row[0] or row[1]
        if requestor_id:
            message = f"Your maintenance request #{request_id} is now in progress."
            cursor.execute("""
                INSERT INTO notifications (user_id, request_id, notification_type, message)
                VALUES (?, ?, ?, ?)
            """, (requestor_id, request_id, "assigned", message))
            conn.commit()
            
            # Send email notification if requestor_email is available
            requestor_email = row[1]
            if requestor_email:
                send_status_notification_email(requestor_email, request_id, 'in_progress', message, row[3] or "")
    
    conn.close()


