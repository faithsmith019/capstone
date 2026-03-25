import streamlit as st

def render_worker():
    st.title("👔 Worker Dashboard")
    st.write("Manage work requests")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        if st.button("📋 View Incoming Requests", use_container_width=True):
            st.session_state['page'] = 'worker_view_upcoming'

    with col2:
        if st.button("📚 View Past Requests", use_container_width=True):
            st.session_state['page'] = 'worker_view_past'

    with col3:
        if st.button("View Assigned Requests", use_container_width=True):
            st.session_state['page'] = 'worker_view_assigned'

      

def showIncomingWorkRequests():
    st.subheader("Work Requests")
    st.write("There are currently no past requests to show.")
    # central database lives in the Data package
    db_path = Path(__file__).parents[1] / "Data" / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, description, status, created_by, assigned_to,
               full_name, phone, date, building, apartment, location
        FROM maintenance_requests 
        WHERE status = 'closed' OR status = 'completed'
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
            'full_name': row[6],
            'phone': row[7],
            'date': row[8],
            'building': row[9],
            'apartment': row[10],
            'location': row[11]
        })
    return requests
def get_requests():
    """Fetch incoming maintenance requests from the database."""
    # central database lives in the Data package
    db_path = Path(__file__).parents[1] / "Data" / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, description, status, created_by, assigned_to,
               full_name, phone, date, building, apartment, location
        FROM maintenance_requests 
        WHERE status = 'open'
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
            'full_name': row[6],
            'phone': row[7],
            'date': row[8],
            'building': row[9],
            'apartment': row[10],
            'location': row[11]
        })
    return requests