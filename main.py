import threading, time, random
import safygiphy, json, requests

from config import Config
from quotes import Quotes
from slackclient import SlackClient

class Shawnbot:
    def __init__(self, quote_list, bot_token):
        self.quote_list = quote_list
        self.slack_client = SlackClient(bot_token)
        self.event = threading.Event()

    def start(self):
        self.slack_client.rtm_connect()
        self.main_thread = threading.Thread(target= self.process_commands)
        self.main_thread.start()    
        
    def stop(self):
        self.event.set()
        self.main_thread.join()

    def process_commands(self):
        print 'Starting thread.'
        
        # Loop waiting for commands
        while True:
            if self.event.isSet():
                break

            try:
                command, channel = self._parse_slack_output(self.slack_client.rtm_read())
            except:
                # Try to open a new connection. This will close if not accessed recently.
                print 'Error reading slack channel. Trying to reconnect.'
                self.slack_client.rtm_connect()
                continue
            if command and channel:
                self._handle_command(command, channel)
            time.sleep(1)
        
        print 'Ending Slack Thread.'
        
    def _handle_command(self, command, channel):
        try:
            # check if it is a slash command
            print command
            if command.startswith(' /'):
                _handle_slash(self, command[1:], channel)
            # It's all upper case
            elif command == command.upper():
                text = "Calm down. Calm down."
                self.slack_client.api_call("chat.postMessage", channel=channel, text=text, as_user=True)
            # Look for keywords
            else:
                for key in self.quote_list.keys():
                    if key.lower() in command.lower():
                        text = random.choice(self.quote_list[key])
                        self.slack_client.api_call("chat.postMessage", channel=channel, text=text, as_user=True)
        except:
            print 'Exception in _handle_command.'
    
    def _parse_slack_output(self, slack_rtm_output):
        # print slack_rtm_output
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'user_profile' in output and output['user_profile']['name'] == 'shawnbot':
                    continue
                if output and 'text' in output:
                    # return text after the @ mention, whitespace removed
                    return output['text'], output['channel']
        return None, None 

    def _handle_slash(self, command, channel):
        if command == 'eye_roll':
            g = safygiphy.Giphy()
            r = g.random(tag="eye-roll")
            payload = {
                'text': r['data']['image_url'],
                'channel': channel
            }

        # send response
        s = json.dumps(payload)
        
        try: 
            print payload
            # r = requests.post(self.slack_webhook_url, data=s)
        except:
            print 'ERROR: Requests threw!'
            
        
        
if __name__ == '__main__':

    print 'Shawnbot starting...'

    # Initialize config
    config = Config()
    config.load_config('.env')

    # Get config variables
    bot_token = config.bot_token
    quote_file = config.quote_file

    # Get Quotes
    _quotes = Quotes()
    _quotes.load_config(quote_file)
    
    shawn_bot = Shawnbot(_quotes.get().quote_list, bot_token)
    shawn_bot.start()
    
    # never return
    resume = threading.Event()
    resume.wait()
    
    raw_input("Press Enter to continue...")
    shawn_bot.stop()
    
