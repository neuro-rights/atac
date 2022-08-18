import os
import random
import sys
import time

# import phonenumbers
from phonenumbers import NumberParseException, phonenumberutil

from ..config.Config import Config


class SendWhatsapp(Config):
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
        self.chat = self.data["chat"]

    if os.environ.get("DISPLAY"):

        def send(self, contacts_file_path, message_file_path):
            """
            Description:
            ------------

            Parameters:
            -----------

            """

            import pywhatkit
            
            msg = "\n".join(self.get_file_content(message_file_path, "message"))
            phone_numbers = self.get_phone_numbers(contacts_file_path)

            # Check you really want to send them
            confirm = input("Send these messages? [Y/n] ")
            if confirm[0].lower() != "y":
                sys.exit(1)
            # Send the messages
            
            for num in phone_numbers:
                try:
                    print("Sending to " + num)
                    pywhatkit.sendwhatmsg_instantly(num, msg, 15, True, 5)
                except Exception as e:
                    print(str(e))
                finally:
                    time.sleep(1)
            #
            print("Exiting!")

