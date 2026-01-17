import smtplib

class EmailClientInterface:

    def __init__(self, email_client, email_account, password, port):
        self.email_account = email_account
        self.password = password
        self.client = email_client
        self.smtp_connection = smtplib.SMTP(email_client, port=port)
        self.smtp_connection.starttls()
        self.smtp_connection.login(user=self.email_account, password=self.password)

    def send_email(self, recipient, message):
        self.smtp_connection.sendmail(
                 from_addr=self.email_account,
                 to_addrs=recipient,
                 msg=message)