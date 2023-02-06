import time
import tweepy

class TweetListener(tweepy.StreamingClient):
    """Handles incoming Tweet stream."""

    def __init__(self, bearer_token, wait_on_rate_limit=True):
        """Create instance variables for tracking number of tweets."""
        super().__init__(bearer_token, wait_on_rate_limit=True)  # call superclass's init

    def on_connect(self):
        """Called when your connection attempt is successful, enabling 
        you to perform appropriate application tasks at that point."""
        print('Connection successful\n')

    def on_tweet(self, tweet):
        """Called when a new tweet arrives."""
        if tweet.referenced_tweets == None:
            print(tweet.text)

            time.sleep(0.2)