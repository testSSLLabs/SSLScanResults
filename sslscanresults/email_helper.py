import smtplib, ssl
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger_helper import logger

SENDER_EMAIL = "test.ssllabs@gmail.com"
RECEIVER_EMAIL = "manoj.cis@gmail.com"
PASSWORD = "qiruqervwennjrzi"

def send_email(html_table_location, sender_email=SENDER_EMAIL, receiver_email=RECEIVER_EMAIL, password=PASSWORD):

    message = MIMEMultipart("alternative")
    message["Subject"] = "SSL Scan Results Report for Domain names"
    message["From"] = sender_email
    message["To"] = receiver_email

    html_text = """\
    <p>Hi,</p>
    <p>Please see below the SSL Scan results for the domains.&nbsp;</p>
    <p>You can also check the reports in CSV, JSON and HTML formats from the below link:</p>
    <p><em><strong><a href="https://github.com/testSSLLabs/SSLLab_hosts_and_report/tree/main/Reports"> ***** Reports in all formats from Github ******</a></strong></em></p>
    <p>Regards,</p>
    <p>Manoj</p>
    """

    try:
        with open(html_table_location) as f:
            html_table = f.read()

        html = html_text+html_table

        # Turn into html MIMEText objects
        part1 = MIMEText(html, "html")

        # Add HTML parts to MIMEMultipart message
        message.attach(part1)
    
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )  
    except Exception as Err:
        logger.error("Email could not be sent due to error: \n{Err}")
        return 1
