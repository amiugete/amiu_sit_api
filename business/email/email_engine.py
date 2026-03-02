import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import logging

load_dotenv()



logger = logging.getLogger(__name__)

# Dati email
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT"))
sender_email = os.getenv("SMTP_SENDER")
recipients = os.getenv("SMTP_RECIPIENTS").split(",")
server_api = os.getenv("SERVER_API")


def send_email_territorio(subject: str, body: str):
    # Frase fissa da aggiungere al corpo
    constant_text = f"\n\nL'utente o IP sta tentando di accedere ai servizi esposti su {server_api}. Si prega di verificare l'identità dell'utente e la legittimità dell'accesso."
    corpo_email = body + constant_text
    # Componi il messaggio
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(corpo_email, "plain"))

    # Invia la mail con gestione eccezioni
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(sender_email, recipients, msg.as_string())
        logger.info("Email inviata con successo a: " + ", ".join(recipients))
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"Errore: destinatari rifiutati - {e}")
    except smtplib.SMTPException as e:
        logger.error(f"Errore SMTP: {e}")
    except Exception as e:
        logger.error(f"Errore generico nell'invio email: {e}")