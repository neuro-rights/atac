import os
import random
import sys
import time

from pytgbot import Bot

from ..config.Config import Config


class SendTelegram(Config):
    """
    Description:
    ------------

    Attributes:
    -----------

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
        self.telegram = self.data["telegram"]
        self.bot = Bot(self.telegram["apikey"])

    def send(self, username, message):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        # sending messages:
        self.bot.send_message(username, message)
   

