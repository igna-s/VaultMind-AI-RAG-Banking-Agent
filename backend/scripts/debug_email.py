import logging

from app.config import settings
from app.services.email import send_verification_email

# Configure logging to stdout
logging.basicConfig(level=logging.DEBUG)


def test_send_verification():
    print("Testing verification email sending...")
    print(f"SMTP Config: User={settings.SMTP_USER}, Host={settings.SMTP_HOST}, Port={settings.SMTP_PORT}")

    test_email = "hua@gmail.com"  # Using an email from credentials.txt or similar, or just a dummy one?
    # Better to use a real one the user can check, or just see if the function errors.
    # The user said "el mail nunca llego".
    # I should try to send to one format that is valid.
    test_email = "noreply.ignasproyect@gmail.com"  # The one in screenshots

    code = "123456"

    print(f"Attempting to send to {test_email}...")
    success = send_verification_email(test_email, code)

    if success:
        print("SUCCESS: Email function returned True.")
    else:
        print("FAILURE: Email function returned False.")


if __name__ == "__main__":
    test_send_verification()
