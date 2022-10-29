from boxman import Config


class InstallManager:
    config: Config

    def __init__(self, config: Config):
        self.config = config

    def install(self):
        pass

    def get_installed(self):
        pass