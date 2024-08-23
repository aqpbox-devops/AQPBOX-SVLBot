import pandas as pd
import argparse
import logging
from constants import *
from typing import List

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import bot.w3_automaton as w3auto

class EmailSender:
    def __init__(self, email, password, smtp, smtp_port=587):
        self.e_from = email
        self.password = password
        self.smtp_server = smtp
        self.smtp_port = smtp_port
        self.payload = MIMEMultipart()

    def attach_text(self, txt: str):
        self.payload.attach(MIMEText(txt, "plain"))

    def attach_file(self, filename: str):
        with open(filename, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            self.payload.attach(part)

    def send(self, subscribers: List[str], subject: str):
        self.payload["From"] = self.e_from
        self.payload["To"] = subscribers[0]
        self.payload["Subject"] = subject
        if len(subscribers) > 1:
            self.payload["Cc"] = ', '.join(subscribers[1:])

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.e_from, self.password)
            server.sendmail(self.e_from, subscribers, self.payload.as_string())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    parser.add_argument('auth_file', type=str, help='Path to the authentication JSON (RUC, Password, ...)')
    parser.add_argument('report_file', type=str, help='Name for the final report file')

    args = parser.parse_args()

    #w3auto.setup_logging(SHAREGS_INFO_LOGS, SHAREGS_WARNING_LOGS)

    print("Before json")

    auth = w3auto.load_json(args.auth_file)

    sender_creds = auth[AUTH_NOTIFICATIONS][AUTH_SENDER]
    email_conn = EmailSender(sender_creds[AUTH_EMAIL], sender_creds[AUTH_PASSWORD],
                             sender_creds[AUTH_SMTP])
    print("Before text attach")
    email_conn.attach_text("Estimado,\nEsto es una prueba.")
    print("Before attach file")
    email_conn.attach_file("../test/out/prueba.xlsx")
    print("Before send")
    email_conn.send(auth[AUTH_NOTIFICATIONS][AUTH_SUBSCRIBER_LIST], "Asunto de prueba 1")

