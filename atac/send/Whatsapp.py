import os
import random
import sys
import time

# import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberType, phonenumberutil

from ..config.Config import Config
from ..util.Util import trace, get_file_content

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

    def get_phone_numbers(self, contact_files_path):
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
        elif os.path.isdir(contact_files_path):
            start_dir = contact_files_path
            for root, dirs, files in os.walk(start_dir):
                for f in files:
                    if f.endswith(".csv"):
                        contact_files.append(os.path.join(root, f))

        lines = []
        for phone_file in contact_files:
            lines += get_file_content(phone_file)

        recipient_phonenumbers = list(
            map(
                lambda z: z.split(",")[1].replace(' ', ''),
                list(
                    filter(
                        lambda x: x.find(",") != -1,
                        lines
                    )
                )
            )
        )

        phone_numbers = []
        for number in recipient_phonenumbers:
            try:
                z = phonenumberutil.parse(number, None)
                if phonenumberutil.number_type(z) == PhoneNumberType.MOBILE:
                    phone_numbers.append(number)
            except NumberParseException as err:
                print("{} - {} is not a mobile phone number".format(err, number))
                pass

        return phone_numbers

    if os.environ.get("DISPLAY"):

        def send(self, contacts_file_path, message_file_path):
            """
            Description:
            ------------

            Parameters:
            -----------

            """

            import pywhatkit
            
            msg = "\n".join(get_file_content(message_file_path))
            phone_numbers = self.get_phone_numbers(contacts_file_path)
            print(phone_numbers)
            # Check you really want to send them
            confirm = input("Send these messages? [y]/n ")
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

