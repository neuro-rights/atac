import time

from ..config.Config import Config


class Send(Config):
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
