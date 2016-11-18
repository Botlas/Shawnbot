import threading, time, random, sys
import safygiphy, json, requests

from config import Config
from quotes import Quotes
from slackclient import SlackClient

def CreateImageAttachment():
    max = 12
    img_url = 'https://github.com/Botlas/Shawnbot/blob/master/images/image%s.png' % random.randint(0,max)

    attachments = {
            "attachments" : [
                {
                    "image_url": img_url,
                    "text": "Jim's Busy."
                }
            ]
        }

    return attachments


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
            	print command
            # It's all upper case
            if command == command.upper():
                text = "Calm down. Calm down."
                self.slack_client.api_call("chat.postMessage", channel=channel, text=text, as_user=True)
            elif 'jimmy' in command.lower():
                self.slack_client.api_call("chat.postMessage", channel=channel, attachments=CreateImageAttachment(), as_user=True)
            # Look for keywords
            else:
                poss = []
                for key in self.quote_list.keys():
                    if key.lower() in command.lower():
                        poss = poss + self.quote_list[key]
                if poss:
                    self.slack_client.api_call("chat.postMessage", channel=channel, text=random.choice(poss), as_user=True)
        except:
            print "Exception in _handle_command:", sys.exc_info()
    
    def _parse_slack_output(self, slack_rtm_output):
        # print slack_rtm_output
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                # if output and 'user_profile' in output and output['user_profile']['name'] == 'shawnbot':
                if output and 'user_profile' in output and 'bot' in output['user_profile']['name']:
                    continue
                if output and 'text' in output:
                    # return text after the @ mention, whitespace removed
                    return output['text'], output['channel']
        return None, None 
        
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
    
    # never return if on heroku
    if config.is_local == False:
        resume = threading.Event()
        resume.wait()
    
    raw_input("Press Enter to continue...")
    shawn_bot.stop()
    
