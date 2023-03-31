from bs4 import BeautifulSoup
from collections import deque
import csv
import os
from requests_html import HTMLSession
import regex as re
from requests import HTTPError
from termcolor import colored
import threading
import tldextract
from torrequest import TorRequest
from urllib.parse import urlsplit
import validators

from ..config.Config import Config


class Scrape(Config):
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
        self.scrape = self.data["scrape"]

        # primary queue (urls to be crawled)
        self.primary_unprocessed_urls = deque()
        self.secondary_unprocessed_urls = deque()

        # visited set (already crawled urls for email)
        self.processed_urls = set()

        # a set of fetched emails
        self.emails = set()
        self.phones = set()
        self.num_phones = 0
        self.num_emails = 0

    def invalid_url(self, url):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        for i in self.scrape["invalid"]["domains"]:
            if i in url.lower():
                print(">>> invalid domain...\n")
                return True

        for j in self.scrape["invalid"]["paths"]:
            if j in url.lower():
                print(">>> invalid path...\n")
                return True

        # reject invalid file types
        for k in self.scrape["invalid"]["files"]:
            if k in url.lower():
                print(">>> invalid file..\n")
                return True

        return False

    @staticmethod
    def make_dirs():
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        if not os.path.isdir(os.getcwd() + "/data/contacts"):
            os.makedirs(os.getcwd() + "/data/contacts")
        if not os.path.isdir(os.getcwd() + "/data/contacts/emails"):
            os.makedirs(os.getcwd() + "/data/contacts/emails")
        if not os.path.isdir(os.getcwd() + "/data/contacts/phones"):
            os.makedirs(os.getcwd() + "/data/contacts/phones")

    @staticmethod
    def truncate_files(data_key):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        csv_path = (
            os.getcwd() + "/data/contacts/emails/" + data_key + "_emails.csv"
        )

        try:
            with open(csv_path, mode="a", newline="") as emails_file:
                emails_file.truncate(0)
                emails_writer = csv.writer(
                    emails_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                )
                emails_writer.writerow(["", "email"])
        except OSError as e:
            print("{} file error {}".format(csv_path, e.errno))
        finally:
            emails_file.close()

        csv_path = (
            os.getcwd() + "/data/contacts/phones/" + data_key + "_phones.csv"
        )

        try:
            with open(csv_path, mode="a", newline="") as phones_file:
                phones_file.truncate(0)
                phones_writer = csv.writer(
                    phones_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                )
                phones_writer.writerow(["", "phone"])
        except OSError as e:
            print("{} file error {}".format(csv_path, e.errno))
        finally:
            phones_file.close()

    @staticmethod
    def extract_emails(content):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        rx_emails = re.compile(
            r"[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+"
            r"(?!jpg|jpeg|png|svg|gif|webp|yji|pdf|htm|title|content|formats)[a-zA-Z]{2,7}"
        )

        return set(
            filter(lambda x: (validators.email(x)), rx_emails.findall(content))
        )

    @staticmethod
    def extract_phones(content):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        rx_phones = re.compile(r"\+(?:[0-9] ?){6,14}[0-9]")

        return set(rx_phones.findall(content))

    def save_email_contacts(self, new_contacts, data_key):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        csv_path = (
            os.getcwd() + "/data/contacts/emails/" + data_key + "_emails.csv"
        )

        try:
            with open(csv_path, mode="a", newline="") as contact_file:
                writer = csv.writer(
                    contact_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                )

                unique_contacts = list(
                    filter(lambda email: email not in self.emails, new_contacts)
                )

                for contact in unique_contacts:
                    print(colored("new email:{0}".format(contact), "white", "on_red"))
                    self.num_emails += 1
                    writer.writerow([self.num_emails, contact.strip()])
        except OSError as e:
            print("{} file error {}".format(csv_path, e.errno))

    def save_phone_contacts(self, new_contacts, data_key):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        csv_path = (
            os.getcwd() + "/data/contacts/phones/" + data_key + "_phones.csv"
        )
        try:
            with open(csv_path, mode="a", newline="") as contact_file:
                writer = csv.writer(
                    contact_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                )

                unique_contacts = list(
                    filter(lambda phone: phone not in self.phones, new_contacts)
                )

                for contact in unique_contacts:
                    print(colored("new phone:{0}".format(contact), "white", "on_red"))
                    self.num_phones += 1
                    writer.writerow([self.num_phones, contact.strip()])
        except OSError as e:
            print("{} file error {}".format(csv_path, e.errno))

    def initialize(self, data_key, starting_url):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        # primary queue (urls to be crawled)
        self.primary_unprocessed_urls.append(starting_url)

        # secondary queue
        self.secondary_unprocessed_urls.clear()

        # visited set (already crawled urls for email)
        self.processed_urls.clear()

        # a set of fetched emails
        self.emails.clear()
        self.phones.clear()

        # make dirs
        self.make_dirs()
        self.truncate_files(data_key)

    def fetch_url(self, url):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        response = None
        try:
            session = HTMLSession()
            response = session.get(url)
            response.html.render()
        except Exception as err:
            print(f"Other error occurred: {err}")
            pass

        session.close()
        return response

    def save_emails_phones(self, data_key, response_text):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        # extract email addresses into the resulting set
        new_emails = self.extract_emails(response_text)
        if new_emails:
            self.save_email_contacts(new_emails, data_key)
            self.emails.update(new_emails)

        # extract phone numbers into resulting set
        new_phones = self.extract_phones(response_text)
        if new_phones:
            self.save_phone_contacts(new_phones, data_key)
            self.phones.update(new_phones)

    def process_links(self, url, links):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        count = 0
        for link in links:

            # link outside search domain
            url_parts = tldextract.extract(url)
            link_parts = tldextract.extract(link)
            if url_parts.domain != link_parts.domain:
                print("link domain is outside domain of url being scraped...")
                continue

            # add link to queue if not in unprocessed list nor in processed list
            if validators.url(link) and link not in self.processed_urls:
                count += 1
                if (
                    count > 20
                    and url not in self.secondary_unprocessed_urls
                ):
                    self.secondary_unprocessed_urls.append(url)
                    if url in self.processed_urls:
                        self.processed_urls.remove(url)
                        break
                elif link not in self.primary_unprocessed_urls:
                    self.primary_unprocessed_urls.append(link)

        if not self.primary_unprocessed_urls:
            print(">>> primary queue empty...\n")
            self.primary_unprocessed_urls.extend(
                self.secondary_unprocessed_urls
            )
            self.secondary_unprocessed_urls.clear()

    def process_page(self, data_key, starting_url):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        status = 0
        self.initialize(data_key, starting_url)

        # process urls 1 by 1 from queue until empty
        while self.primary_unprocessed_urls:

            # move next url from queue to set of processed urls
            url = self.primary_unprocessed_urls.popleft()
            print(colored("{0} urls:{1} {2} | emails:{3} phones:{4} - {5}".format(
                    threading.get_native_id(),
                    len(self.primary_unprocessed_urls),
                    len(self.secondary_unprocessed_urls),
                    len(self.emails),
                    len(self.phones),
                    url,
                ),
                "white",
                "on_green"
            ))

            self.processed_urls.add(url)

            # skip if invalid
            if self.invalid_url(url):
                continue

            response = self.fetch_url(url)
            if response:
                self.save_emails_phones(data_key, response.text)
                links = response.html.absolute_links
                self.process_links(url, links)

        return status
