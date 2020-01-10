import os
import time
import re
from slackclient import SlackClient


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM


def respond(response, channel):
    """
        Executes bot command if the command is known
    """

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response,
        unfurl_links=True
    )


def parse_arxiv_mention(msg):
    return_msg = None

    # first replace arxiv urls
    regex = re.compile('.*arxiv.org/pdf/(.+)\\.pdf.*')
    #regex = re.compile('.*<https://arxiv.org/pdf/(.+)\\.pdf>.*')
    match = regex.match(msg)
    if match:
        for i in range(1, len(match.groups)):
            article = match.group(i)
            vers_regex = re.compile('^(.*)v[0-9]$')
            vers_match = vers_regex.match(article)
            lean_article = article
            if vers_match:
                lean_article = vers_match.group(1)
            #return_msg = msg.replace(f'<https://arxiv.org/pdf/{article}.pdf>', f'https://arxiv.org/abs/{lean_article}')
            return_msg = msg.replace(f'arxiv.org/pdf/{article}.pdf', f'arxiv.org/abs/{lean_article}')


    # next replace openreview urls
    regex = re.compile('.*openreview.net/pdf.id.*')
    match = regex.match(msg)
    if match:
        if return_msg is None:
            return_msg = msg
        return_msg = return_msg.replace('openreview.net/pdf?id=', 'openreview.net/forum?id=')
    
    return return_msg

def parse_message(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            message = parse_arxiv_mention(event["text"])
            if message:
                return message, event["channel"]
    return None, None


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("ArxivBot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        bot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            msg = slack_client.rtm_read()
            response, channel = parse_message(msg)
            if response:
                respond(response, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
