__author__ = 'Andrew Quel'

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class FileIsEmptyError(ValueError):
    pass


def email_message(sender, subject, messageFile, *recipients):
    """
    Returns MIMEMultipart message with simple text email message that is ready to be sent with send_email()
    :param sender: string, e-mail address to be used as sender
    :param subject: string, subject of a message
    :param messageFile: string, file path to text file with message
    :param recipients: list/tuple or comma separated params of strings with recipients e-mail addresses

    This function may rise the following exceptions:
        FileNotFoundError    when file doesn't exist
        FileIsEmptyError     when file is empty
        IOError              when file cannot be opened for 'read'
    """

    # Create Message
    msg = MIMEMultipart()

    # Set it's header fields
    msg['From'] = sender
    msg['Subject'] = subject

    # Set recipients as one string, separate e-mails with commas
    msg['To'] = ", ".join(recipients)

    # Open given file, thrown exceptions when it's not found, empty or can't be opened
    if not os.path.exists(messageFile):
        raise FileNotFoundError()
    elif not os.path.getsize(messageFile):
        raise FileIsEmptyError()

    file = open(messageFile)
    msg.attach(MIMEText(file.read()))
    file.close()

    return msg


def send_email(message, user=None, password=None, server='smtp.gmail.com', port=587):
    """
    :param message: MIMEMultipart message, i.e. from email_message function
    :param user: username for the login on SMTP server
    :param password: password for the login on SMTP server
    :param server: (optional) string, server from where you will be sending the email
    :param port, (optional) int, network port for server
    """

    # Create server object
    mailServer = smtplib.SMTP(server, port)

    try:
        # Connect to SMTP server using created object & login
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()

        if user and password:
            mailServer.login(user, password)

        # Get sender & recipient from message
        recipientList = message["To"].split(", ")

        # Send e-mail
        mailServer.sendmail(message["From"], recipientList, str(message))

    finally:
        # Close connection to remote SMTP server
        mailServer.close()

if __name__ == '__main__':
    msg = email_message("umpalumpa@gogo.com", "Testo-Presto", "message.txt", "andrew.quel@gmail.com")
    send_email(msg, "andrewquelsmtp@gmail.com","mailgooglecom")