import os

class Config:
    _instance = None

    def load_config(self, config_path):
        env = {}
        is_local = False
        if not 'DYNO' in os.environ:
            is_local = True
            if not os.path.exists(config_path):
                print 'please create a .env file in this directory in order to run locally!'
                exit(-1)

        # used for local testing without starting up heroku
        if is_local:
            env = {}
            print 'running locally, reading config from %s' % config_path
            with open(config_path, 'r') as fp:
                for line in fp:
                    idx = line.index('=')
                    key = line[:idx]
                    value = line[idx + 1:].strip()
                    env[key] = value
        else:
            logger.info('running on heroku, reading config from environment')
            env = os.environ
        
        try:
            self.bot_token = str(env['BOT_TOKEN'])
            self.quote_file = str(env['QUOTE_FILE'])
        except KeyError as ke:
            logging.error('key must be defined in config: %s!', ke)
            exit(-1)

        Config._instance = self
        
    @staticmethod
    def get():
        return Config._instance
