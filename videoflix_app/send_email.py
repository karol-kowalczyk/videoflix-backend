import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# E-Mail-Daten
sender_email = "test@example.com"
receiver_email = "user@example.com"
subject = "Test"
body = "Testnachricht"

# Erstelle die E-Mail-Nachricht
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject

# Füge den Nachrichtentext hinzu
msg.attach(MIMEText(body, 'plain'))

# Verbindung zum lokalen SMTP-Server herstellen
try:
    with smtplib.SMTP('127.0.0.1', 1025) as server:
        # Sende die E-Mail
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("E-Mail erfolgreich gesendet!")
except Exception as e:
    print(f"Fehler beim Senden der E-Mail: {e}")