__author__ = 'Andrew Quel'

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from optparse import OptionParser, OptionGroup


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


# Main flow of execution when launched as aq.py (not imported as module)
if __name__ == '__main__':

    # Prepare usage & description text for --help argument
    helpUsage = "%prog -m message.txt -s 'Subject' -f 'sender@me.com' -t 'recipient@they.com'"
    helpDescription = """Connects to remote SMTP server & sends plain text message
    You can use this gmail account for auth:
    andrewquelsmtp@gmail.com
    mailgooglecom
    """

    # Setup parser to show help, description & parse options
    parser = OptionParser(usage=helpUsage, description=helpDescription)
    parser.add_option("-m", "--message", dest="filename", help="Read e-mail message from FILE", metavar="FILE")
    parser.add_option("-s", "--subject", dest="subject", default="No Subject", help="Subject of E-mail")
    parser.add_option("-f", "--from", dest="sender", help="Sender's Email address")
    parser.add_option("-t", "--to", dest="recipient", help="E-mail address of a recipient")

    # Setup optional options, which can be omitted
    optionalGroup = OptionGroup(parser, "Optional")
    optionalGroup.add_option("-u", "--user", dest="user", default=None, help="User for auth on server.")
    optionalGroup.add_option("-p", "--password", dest="password", default=None, help="Password for auth on server.")
    optionalGroup.add_option("--server", dest="server", default=None, help="Server URL.")
    optionalGroup.add_option("--port", dest="port", default=None, help="Server port.")
    parser.add_option_group(optionalGroup)

    # Parse command line arguments
    (options, args) = parser.parse_args()
    sender = options.sender
    subject = options.subject
    filename = options.filename
    recipient = options.recipient

    # Bail out if we don't have required parameters
    if not (sender and subject and filename and recipient):
        print("Sender, Subject, Filename & Recipient must be set!")
        exit()

    # Prepare & Send Message
    print('Preparing Message...')
    try:
        msg = email_message(sender, subject, filename, recipient)
        print('Sending...')
        send_email(msg, options.user, options.password)
        print('Message Sent!')
        
    # Handle all possible errors & log them
    except FileNotFoundError:
        print('File %s not found!' % filename)
    except FileIsEmptyError:
        print('File %s is empty!' % filename)
    except IOError:
        print("Can't open %s" % filename)
    except smtplib.SMTPHeloError:
        print("SMTP Server Error: The server didn't reply properly to the 'hello' greeting")
    except smtplib.SMTPAuthenticationError:
        print ("SMTP Server Error: The server didn't accept the username/password combination.")
    except smtplib.SMTPRecipientsRefused:
        print("The server rejected ALL recipients (no mail was sent)")
    except smtplib.SMTPSenderRefused:
        print("The server didn't accept the from_addr.")
    except smtplib.SMTPDataError:
        print("The server replied with an unexpected error code (other than a refusal of a recipient).")
    except smtplib.SMTPException:
        print("SMTP Server Error: No suitable authentication method was found")