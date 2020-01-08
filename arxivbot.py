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
        text=response
    )


def parse_arxiv_mention(msg):
    regex = re.compile('.*arxiv.org/pdf/(.+)\\.pdf.*')
    match = regex.match(msg)
    if match:
        article = match.group(1)
        msg = msg.replace(f'arxiv.org/pdf/{article}.pdf', f'arxiv.org/abs/{article}')
        return msg
    return None

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
