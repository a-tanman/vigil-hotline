import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email.mime.base import MIMEBase
from email import encoders

import time
import re
import os
import ctypes


# Send email from the Gmail email, SMTP
# To_recipients - Comma separated list of emails.
# Subject - Email Subject
# HTML_Text - Text in HTML to be sent.
# Attachement_Name - Attachment List.
# Send_Email(Email_List,[], Email_Title_String, Email_html, [])
def Send_Email(To_recipients , cc_recipients, Subject ,HTML_Text, Attachment_Name):

    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()           # Hello to SMTP server
    server.starttls()       # Need to start the TLS connection
    server.login("aaron.limzy@gmail.com", "ReportReport")   #Login with credientials

    me = "aaron.limzy@gmail.com"
    you = To_recipients

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Subject
    msg['From'] = me
    msg['To'] = ",".join(To_recipients)
    msg['cc'] = ",".join(cc_recipients)

    for i in range(len(Attachment_Name)):
        Buffer = Attachment_Name[i].split('/')
        filename = Buffer[len(Buffer)-1]
        attachment = open(Attachment_Name[i], "rb")
        part=MIMEBase('application','octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        #Only Want to add the part of the name where it is the excel name.
        part.add_header('Content-Disposition', "attachment; filename= " + filename.split("\\")[len(filename.split("\\"))-1])
        msg.attach(part)

    p = MIMEText(HTML_Text, 'html')
    msg.attach(p)
    server.sendmail(me, To_recipients + cc_recipients , msg.as_string())


