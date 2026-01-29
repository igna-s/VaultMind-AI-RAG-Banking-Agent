import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def send_reset_email(to_email: str, token: str):
    """
    Sends a password reset email using Gmail SMTP.
    """
    print(f"DEBUG: Attempting to send reset email to {to_email}")
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning("SMTP not configured. Skipping email send.")
        print(f"DEBUG: Password reset token for {to_email}: {token}")
        return False

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = "Recuperación de Contraseña - VaultMind AI"

        # Email body
        # Assuming frontend runs on localhost:5173 for now, or use a setting for FRONTEND_URL
        reset_link = f"http://localhost:5173/reset-password?token={token}"
        
        body = f"""
        <html>
            <body>
                <h2>Recuperación de Contraseña</h2>
                <p>Hola,</p>
                <p>Hemos recibido una solicitud para restablecer tu contraseña en VaultMind AI.</p>
                <p>Haz clic en el siguiente enlace para continuar:</p>
                <p><a href="{reset_link}">Restablecer Contraseña</a></p>
                <p><small>Si no solicitaste esto, ignora este mensaje.</small></p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Send email
        print("DEBUG: Connecting to SMTP server...")
        print("DEBUG: Connecting to SMTP server...")
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        print("DEBUG: Logging into SMTP...")
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        print("DEBUG: Sending email...")
        server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Reset email sent to {to_email}")
        print("DEBUG: Email sent successfully!")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        print(f"CRITICAL ERROR Sending Email: {e}")
        return False

def send_verification_email(to_email: str, code: str):
    """
    Sends a verification code email using Gmail SMTP.
    """
    print(f"DEBUG: Attempting to send verification email to {to_email}")
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning("SMTP not configured. Skipping email send.")
        print(f"DEBUG: Verification code for {to_email}: {code}")
        return False


    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = "Verifica tu cuenta - VaultMind AI"

        # Email body
        body = f"""
        <html>
            <body>
                <h2>Verificación de Cuenta</h2>
                <p>Hola,</p>
                <p>Gracias por registrarte. Tu código de verificación es:</p>
                <h1 style="color: #4f46e5; letter-spacing: 5px;">{code}</h1>
                <p><small>Este código expirará en 15 minutos.</small></p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

    

        # Send email
        print("DEBUG: Connecting to SMTP server for verification...")
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        print("DEBUG: Logging into SMTP...")
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        print("DEBUG: Sending verification email...")
        server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Verification email sent to {to_email}")
        print("DEBUG: Verification email sent successfully!")
        return True

    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        print(f"CRITICAL ERROR Sending Verification Email: {e}")
        return False
