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

        try:

            print(";".join(mailing_list))
            envelope = Envelope().message(html_content).subject(subject)
            envelope = envelope.from_(auth["sender"]).to(";".join(mailing_list))
            envelope = envelope.smtp(auth["server"], auth["port"], auth["user"], auth["password"])

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

                #self.send_email_twisted(email_batch, message_content, subject)

                progress.update(1)
                #print("Sleeping for {} seconds...".format(self.email["emailthrottleinterval"]))
                #print("To change the throttle value edit your json config file")
                #time.sleep(self.email["emailthrottleinterval"])

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
