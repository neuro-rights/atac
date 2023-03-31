import tweepy

from ..config.Config import Config


class SendTwitter(Config):
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
        self.config = self.data["twitter"]
 
        """
        self.client = tweepy.Client(access_token=self.config["accesstoken"],
                            access_token_secret=self.config["accesstokensecret"],
                            consumer_key=self.config["consumerkey"],
                            consumer_secret=self.config["consumersecret"])
        """

        auth = tweepy.OAuth1UserHandler(
            self.config["consumerkey"], self.config["consumersecret"],
            self.config["accesstoken"], self.config["accesstokensecret"]
        )
        self.client = tweepy.API(auth)

    def send(self, text, media_path=None):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        for handle in self.config["handles"]:
            print(self.config["handles"])
            message = "{} {}".format(handle, text)
            print("{} {}".format(len(message), message))
            if 300 < len(message):
                print("message too long > 300 characters. Please rewrite message")
                break
            response = self.client.update_status(message)
            print(response)

