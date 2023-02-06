import time
import tweepy

class TweetListener(tweepy.StreamingClient):
    """Handles incoming Tweet stream."""

    def __init__(self, bearer_token):
        super().__init__(bearer_token, wait_on_rate_limit=True)

    def on_connect(self):
        print('Connection successful\n')

    def on_tweet(self, tweet):
        """Called when a new tweet arrives."""
        if tweet.referenced_tweets == None:
            print(tweet.text)

            time.sleep(0.2)