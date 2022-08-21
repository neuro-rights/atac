from __future__ import print_function

import base64
from envelope import Envelope
import getpass
import io
import logging
import json
import mistune
import os
import random
import re
import ssl
import sys
import time
from termcolor import colored
from tqdm import tqdm
import validators

from OpenSSL.SSL import SSLv3_METHOD

from twisted.mail.smtp import ESMTPSenderFactory
from twisted.python.usage import Options, UsageError
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.defer import Deferred
from twisted.internet import reactor

from email.mime.text import MIMEText

from ..config.Config import Config
from ..compose.Compose import Compose
from ..util.Util import trace, get_file_content


class SendEmail(Config):
    """
    Description:
    ------------

    Attributes:
    ----------

    Methods:
    --------
    """

    def __init__(
        self,
        encrypted_config=True,
        config_file_path="auth.json",
        key_file_path=None,
    ):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        super().__init__(encrypted_config, config_file_path, key_file_path)
        self.load_config(config_file_path)
        self.email = self.data["email"]

    def get_config(self):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        content_index = int(self.email["activecontent"])
        auth_index = int(self.email["activeauth"])

        if auth_index > len(self.email["auth"]):
            print("Invalid activeauth index in your .json config")
            sys.exit(1)

        if content_index > len(self.email["content"]):
            print("Invalid activecontent index in your .json config")
            sys.exit(1)

        content = self.email["content"][content_index]
        auth = self.email["auth"][auth_index]

        return auth, content

    def update_config(self):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        auth, content = self.get_config()
        # set active to next and save config
        if self.email["rotatecontent"]:
            self.email["activecontent"] = (
                1 + self.email["activecontent"]
            ) % len(content)

        # set active auth to next and save config
        if self.email["rotateauth"]:
            self.email["activeauth"] = (1 + self.email["activeauth"]) % len(
                auth
            )

        self.save_config(self.config_file_path, self.encrypted_config)

    def get_contact_files(self, contact_files_path):
        """
        Description: Get contact files

        Parameters
        ----------
        contact_files_path : str    The path to the contacts CSV
        """

        contact_files = []
        start_dir = "data/contacts/emails"

        if os.path.isfile(contact_files_path):
            contact_files.append(contact_files_path)
            return contact_files
        elif os.path.isdir(contact_files_path):
            start_dir = contact_files_path

        for root, dirs, files in os.walk(start_dir):
            for f in files:
                if f.endswith(".csv"):
                    contact_files.append(os.path.join(root, f))

        return contact_files

    def sendmail(self, authenticationUsername, authenticationSecret, fromAddress, toAddress, messageFile, smtpHost, smtpPort=25):
        """
        @param authenticationUsername: The username with which to authenticate.
        @param authenticationSecret: The password with which to authenticate.
        @param fromAddress: The SMTP reverse path (ie, MAIL FROM)
        @param toAddress: The SMTP forward path (ie, RCPT TO)
        @param messageFile: A file-like object containing the headers and body of
        the message to send.
        @param smtpHost: The MX host to which to connect.
        @param smtpPort: The port number to which to connect.

        @return: A Deferred which will be called back when the message has been
        sent or which will errback if it cannot be sent.
        """

        # Create a context factory which only allows SSLv3 and does not verify
        # the peer's certificate.
        #contextFactory = ClientContextFactory()
        #contextFactory.method = SSLv3_METHOD
        resultDeferred = Deferred()
        senderFactory = ESMTPSenderFactory(
            authenticationUsername,
            authenticationSecret,
            fromAddress,
            toAddress,
            messageFile,
            resultDeferred,
            heloFallback=True,
            requireAuthentication=True,
            requireTransportSecurity=False)

        #reactor.connectSSL(smtpHost, smtpPort, senderFactory, ClientContextFactory())
        reactor.connectTCP(smtpHost, smtpPort, senderFactory)

        return resultDeferred

    def cbSentMessage(self, result):
        """
        Called when the message has been sent.

        Report success to the user and then stop the reactor.
        """
        print("Message sent")
        reactor.stop()

    def ebSentMessage(self, err):
        """
        Called if the message cannot be sent.

        Report the failure to the user and then stop the reactor.
        """
        err.printTraceback()
        reactor.stop()

    def send_email_twisted(self, mailing_list, message_content, subject):
        
        auth, _ = self.get_config()    
        
        message = MIMEText("https://github.com/neuro-rights/atac/blob/main/MOTIVATION.md")
        message["Subject"] = subject
        message["From"] = auth["sender"]
        message["To"] = "; ".join(mailing_list)

        result = self.sendmail(
            auth["user"],
            auth["password"],
            auth["sender"],
            "; ".join(mailing_list), 
            io.StringIO("Test"),
            auth["server"],
            auth["port"]
        )
        result.addCallbacks(self.cbSentMessage, self.ebSentMessage)
        reactor.run()

    def send_email(self, mailing_list, message_content, subject):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        status = 0
        auth, _ = self.get_config()
        html_content = Compose.md2html(message_content)

        auth_obj = dict(host=auth["server"], port=auth["port"], attempts=3, delay=3)
        if "user" in auth:
            auth_obj["user"]=auth["user"]
        if "password" in auth:
            auth_obj["password"]=auth["password"]
        if "security" in auth:
            auth_obj["security"]=auth["security"],

        try:

            print(";".join(mailing_list))
            envelope = Envelope().message(html_content).subject(subject)
            envelope = envelope.from_(auth["sender"]).to(";".join(mailing_list))
            envelope = envelope.smtp(auth_obj)

            recipients_status = envelope.check(check_mx=True, check_smtp=True)
            print(recipients_status)

            envelope.send(send=False).send(send=True)

        except Exception as err:
            status = err

        return status

    def send_emails_in_buckets(self, email_batches, message_file_path, subject):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(subject)
        auth, _ = self.get_config()
        encrypted_emails = []
        message_content = get_file_content(message_file_path)
        print("sending email batches…")

        with tqdm(total=len(email_batches)) as progress:
            for email_batch in email_batches:

                send_status = self.send_email(email_batch, message_content, subject)
                if send_status != 0:
                    print(colored("An error occurred: {}".format(send_status), "white", "on_red"))

                # self.send_email_twisted(email_batch, message_content, subject)

                progress.update(1)
                print("Sleeping for {} seconds...".format(self.email["emailthrottleinterval"]))
                print("To change the throttle value edit your json config file")
                time.sleep(self.email["emailthrottleinterval"])

    def store_emails_in_buckets(self, lines):
        """
        Description:    Store emails in buckets
        ------------

        Parameters:
        -----------
        lines : list    The contacts list
        """
        auth, content = self.get_config()
        recipient_emails = list(
            map(
                lambda z: z.split(",")[1],
                list(
                    filter(
                        trace(
                            lambda x: x.find(",") != -1
                            and validators.email(x.split(",")[1])
                        ),
                        lines,
                    )
                ),
            )
        )

        random.seed()
        random.shuffle(recipient_emails)

        batch_emails = [
            [
                recipient
                for recipient in recipient_emails[
                    start_ndx : None
                    if len(recipient_emails[start_ndx:])
                    < self.email["maxrecipients"]
                    else start_ndx + self.email["maxrecipients"]
                ]
            ]
            for start_ndx in range(
                0, len(recipient_emails), self.email["maxrecipients"]
            )
        ]
        #print(json.dumps(batch_emails, indent=4))
        return batch_emails

    def send(self, email_files_path, message_file_path, subject):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        contact_files_paths = self.get_contact_files(email_files_path)
        print(json.dumps(contact_files_paths, indent=4))
        for ef in contact_files_paths:
            print(contact_files_paths)
            email_list = get_file_content(ef)
            email_buckets = self.store_emails_in_buckets(email_list)
            self.send_emails_in_buckets(
                email_buckets, message_file_path, subject
            )
