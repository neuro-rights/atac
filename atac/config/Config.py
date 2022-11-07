import os
import sys
import json
import stdiomask
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import inspect

from pathlib import Path

from .settings import (
    chat_settings,
    compose_settings,
    email_settings,
    irc_settings,
    scrape_settings,
    twitter_settings,
    tor_settings,
)

from abc import ABCMeta, abstractmethod


class Config(metaclass=ABCMeta):
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

        self.key = None
        self.data = None
        self.encrypted_config = encrypted_config
        self.key_file_path = key_file_path

        if encrypted_config and self.key_file_path:
            self.load_key(self.key_file_path)
            print(self.key)

        if encrypted_config and not self.key:
            self.generate_key()

        self.config_file_path = Path(config_file_path)

    def generate_key(self):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(inspect.stack()[1].function)
        if "GITHUB_ACTION" in os.environ:
            password = bytes("M4m4k154n", encoding="utf-8")
            salt = bytes("77", encoding="utf-8")
        else:
            password = bytes(
                stdiomask.getpass(prompt="\nEnter password - ", mask="*"),
                encoding="utf-8",
            )
            salt = bytes(
                stdiomask.getpass(prompt="Enter Salt (optional) - ", mask="*"),
                encoding="utf-8",
            )
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(password))

    def load_key(self, key_file_path):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        try:
            with open(key_file_path, "rb") as key_file:
                self.key = key_file.read()
        except OSError as e:
            print("{} file error {}".format(key_file_path, e.errno))

    def save_key(self, key_file_path):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        try:
            with open(key_file_path, "wb") as key_file:
                key_file.write(self.key)
        except OSError as e:
            print("{} file error {}".format(key_file_path, e.errno))

    def save_config(self, config_file_path, encrypted_config):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        data = None

        if encrypted_config:
            fernet = Fernet(self.key)
            # encrypting the file
            data = fernet.encrypt(
                json.dumps(self.data, ensure_ascii=False).encode("utf-8")
            )
        else:
            data = json.dumps(self.data, ensure_ascii=False, indent=4).encode(
                "utf-8"
            )

        # opening the file in write mode and writing the encrypted data
        try:
            with open(config_file_path, "wb") as config_file:
                config_file.write(data)
        except OSError as e:
            print("{} file error {}".format(config_file_path, e.errno))

    def load_config(self, config_file_path="auth.json"):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        if not os.path.isfile(config_file_path):
            self.new_config(config_file_path)

        data = None
        config_file = None

        try:
            with open(config_file_path, "rb") as config:
                config_file = config.read()
        except OSError as e:
            print("{} file error {}".format(self.config_file_path, e.errno))

        # decrypting the file
        if self.encrypted_config:
            try:
                fernet = Fernet(self.key)
                self.data = json.loads(fernet.decrypt(config_file))
            except InvalidToken:
                print("Invalid Key - Unsuccessfully decrypted")
                sys.exit(1)
        else:
            self.data = json.loads(config_file)

        # print(json.dumps(self.data, indent=4))
            

    def dict_from_module(self, module):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        context = {}
        for setting in dir(module):
            # you can write your filter here
            if setting.islower() and setting.isalpha():
                context[setting] = getattr(module, setting)

        return context

    def add_email_auth(self):
        """
        Description:
        ------------

        Parameters:
        -----------

        """
        if "GITHUB_ACTION" in os.environ:
            return

        email_user = input("mail User: ")
        email_password = stdiomask.getpass("mail Password: ")
        email_port = input("mail Port: ")
        email_sender = input("mail Sender: ")
        email_server = input("mail Server: ")
        email_security = input("mail Security (tls/ssl): ")

        email_auth = dict(
            user=email_user,
            password=email_password,
            port=email_port,
            sender=email_sender,
            server=email_server,
            security=email_security,
        )

        return email_auth

    def add_irc_auth(self):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        if "GITHUB_ACTION" in os.environ:
            return

        irc_server_hostname = input("IRC Server Hostname: ")
        irc_server_security = input("IRC Security (plaintext/ssl): ")
        irc_server_ssl = True if irc_server_security == "ssl" else False
        irc_server_port = 6697 if irc_server_security == "ssl" else 6667
        irc_server_nick = input("IRC Nick: ")
        irc_server_password = stdiomask.getpass("IRC Password: ")

        irc_auth = dict(
            active=True,
            nickname=irc_server_nick,
            password=irc_server_password,
            port=irc_server_port,
            server=irc_server_hostname,
            ssl=irc_server_ssl,
        )

        return irc_auth

    def new_config(self, config_file_path):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        if "GITHUB_ACTION" in os.environ:
            if "MAIL_USER" not in os.environ:
                print("MAIL_USER is unset")
                sys.exit(1)
            if "MAIL_PASSWORD" not in os.environ:
                print("MAIL_PASSWORD is unset")
                sys.exit(1)
            if "MAIL_SERVER" not in os.environ:
                print("MAIL_SERVER is unset")
                sys.exit(1)
            if "MAIL_PORT" not in os.environ:
                print("MAIL_PORT is unset")
                sys.exit(1)
            if "MAIL_SECURITY" not in os.environ:
                print("MAIL_SECURITY is unset")
                sys.exit(1)

        chat = dict(chat=self.dict_from_module(chat_settings))
        compose = dict(compose=self.dict_from_module(compose_settings))
        email = dict(email=self.dict_from_module(email_settings))
        irc = dict(irc=self.dict_from_module(irc_settings))
        scrape = dict(scrape=self.dict_from_module(scrape_settings))
        twitter = dict(twitter=self.dict_from_module(twitter_settings))
        tor = dict(tor=self.dict_from_module(tor_settings))
        self.data = dict(
            **chat, **compose, **email, **irc, **scrape, **twitter, **tor
        )
        
        print(os.environ)
        if not "GITHUB_ACTION" in os.environ:
            do_email_auth = input("would you like to add an email account (Y/N)? ")
            if do_email_auth == "Y":
                email_auth = self.add_email_auth()
                self.data["email"]["auth"].append(email_auth)

            do_irc_auth = input("would you like to add an irc account (Y/N)? ")
            if do_irc_auth == "Y":
                irc_auth = self.add_irc_auth()
                self.data["irc"]["networks"].append(irc_auth)

        self.save_config(config_file_path, self.encrypted_config)
