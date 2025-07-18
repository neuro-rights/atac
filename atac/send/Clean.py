import os
import csv
from tqdm import tqdm

import validators

"""
from validators import ValidationError
"""

import phonenumbers
from phonenumbers import NumberParseException, phonenumberutil

from ..config.Config import Config


class Clean(Config):
    """
    Description:
    ------------

    Attributes:
    ----------

    Methods:
    --------
    """

    @staticmethod
    def clean_phones(path):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        print(path)
        # get mailing list csv files
        ml_files = list(filter(lambda c: c.endswith(".csv"), os.listdir(path)))
        for ml in ml_files:
            cf = path + ml
            print(cf)
            # read
            with open(cf) as file:
                lines = file.readlines()
                with tqdm(total=len(lines)) as progress:
                    for _, phone in csv.reader(lines):
                        print(phone)
                        try:
                            z = phonenumbers.parse(phone)
                            valid_number = phonenumbers.is_valid_number(z)
                            if valid_number:
                                line_type = phonenumberutil.number_type(z)
                                print(line_type)
                        except NumberParseException as e:
                            print(str(e))

    @staticmethod
    def clean_emails(path):
        """
        Description:
        ------------

        Parameters:
        -----------

        """
        
        print(path)
        # get mailing list csv files
        ml_files = list(filter(lambda c: c.endswith(".csv"), os.listdir(path)))
        for ml in ml_files:
            cf = path + ml
            print(cf)
            ml_emails = []
            # read
            with open(cf) as file:
                lines = file.readlines()
                with tqdm(total=len(lines)) as progress:
                    for ndx, receiver_email in csv.reader(lines):
                        if validators.email(receiver_email):
                            ml_emails.append(
                                {"index": ndx, "email": receiver_email}
                            )
                        else:
                            print("{0} INVALID".format(receiver_email))
                        progress.update(1)
            # write
            with open(cf, mode="a") as file2:
                file2.truncate(0)
                with tqdm(total=len(ml_emails)) as progress2:
                    writer = csv.writer(
                        file2,
                        delimiter=",",
                        quotechar='"',
                        quoting=csv.QUOTE_MINIMAL,
                    )
                    writer.writerow(["", "email"])
                    for item in ml_emails:
                        writer.writerow([item["index"], item["email"]])
                        progress2.update(1)
