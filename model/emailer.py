import aiosmtplib
import os
import configparser

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = configparser.ConfigParser()
config.read(os.getenv("SECRET_PATH"))
my_email = config["email"]["sender"]
my_password = config["email"]["password"]


async def send_email(to, subject, message):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = my_email
    msg['To'] = to
    part = MIMEText(message, 'html')
    msg.attach(part)

    server = aiosmtplib.SMTP('smtp.gmail.com', 587)
    await server.connect()
    await server.starttls()
    try:
        await server.login(my_email, my_password)
        await server.sendmail(my_email, to, msg.as_string())
        print("Email sent!")
        return True
    except Exception as e:
        print(str(e))
        return False
    finally:
        await server.quit()
