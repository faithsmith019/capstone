import streamlit as st
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(email_sender: str, password: str, email_receiver: str, subject: str, body: str):
    """Send an email with SMTP using provided credentials.
    
    Inputs:
        email_sender: sender email address.
        password: sender email password or app-specific password.
        email_receiver: recipient email address.
        subject: email subject line.
        body: email body text.
    Returns:
        Tuple[bool, str] indicating success and a message.
    """
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, password)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)


def send_status_notification_email(requestor_email: str, request_id: int, status: str, message: str, requestor_name: str = ""):
    """Send a status change email to a requestor using environment credentials.

    Inputs:
        requestor_email: recipient email address.
        request_id: maintenance request ID.
        status: new status string.
        message: body message text.
        requestor_name: optional name used in greeting.
    Outputs:
        Sends email via SMTP and returns success state and info text.
    """
    email_sender = os.getenv('EMAIL_SENDER', '')
    password = os.getenv('EMAIL_PASSWORD', '')
    if not email_sender or not password:
        return False, "Missing EMAIL_SENDER or EMAIL_PASSWORD environment variables"

    subject = f"Maintenance Request #{request_id} status updated to {status}"
    greeting = f"Dear {requestor_name}," if requestor_name else "Dear resident,"
    body = f"{greeting}\n\n{message}\n\nWe appreciate your patience and are working diligently to resolve your maintenance needs.\n\nThank you,\nMaintenance Team"

    return send_email(email_sender, password, requestor_email, subject, body)


def email_service_ui():
    """Render a manual email sending UI for administrators or debugging.

    Inputs: sender, receiver, subject, body, and password entered in the UI.
    Output: sends an email via send_email when the button is clicked.
    """
    st.title("📧 Send Manual Email")
    email_sender = st.text_input("From")
    email_receiver = st.text_input("To")
    subject = st.text_input("Subject")
    body = st.text_area("Body")
    password = st.text_input("Password", type="password")

    if st.button("Send Email"):
        success, info = send_email(email_sender, password, email_receiver, subject, body)
        if success:
            st.success(info)
        else:
            st.error(f"Failed to send email: {info}")  

