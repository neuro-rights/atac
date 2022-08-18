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

        self.auth = tweepy.OAuthHandler(self.config['consumer_key'], self.config['consumer_secret'])
        self.auth.set_access_token(self.config['access_token'], self.config['access_token_secret'])
        self.twitter = tweepy.API(self.auth)


    def compose_message(self, message):
        pass

    def send(self, message, image=None):
        """
        Description:
        ------------

        Parameters:
        -----------

        """

        if image:
            self.twitter.update_with_media(image, message)
        else:
            self.twitter.update_status(message)

