import tweepy

class TweetListener(tweepy.StreamingClient):
    """Handles incoming Tweet stream."""

    def __init__(self, bearer_token, counts_dict, tweets_list, topic, limit):
        """Configure the TweetListener."""
        self.tweets_list = tweets_list
        self.counts_dict = counts_dict
        self.topic = topic
        self.tweet = ''
        self.fields = {}
        self.TWEET_LIMIT = limit
        super().__init__(bearer_token, wait_on_rate_limit=True)

    def on_connect(self):
        print('Connection successful\n')

    def on_tweet(self, tweet):
        """Called when a new tweet arrives."""
        if tweet.referenced_tweets == None:
            if (tweet.text.startswith('RT') or
                self.topic.lower() not in tweet.text.lower()):
                return
            
            self.counts_dict['total_tweets'] += 1
            self.tweet = tweet.text

        if self.counts_dict['locations'] < self.TWEET_LIMIT:
            self.disconnect()
            return

    def on_includes(self, includes):
        """Called when a new includes object arrives."""
        if not includes.get('places'):
            return
        self.counts_dict['locations'] += 1
        self.fields['username'] = includes['users'][0]['username']
        self.fields['text'] = self.tweet
        self.fields['location'] = includes['places'][0]['full_name']
        self.tweets_list.append(self.fields)
        self.fields = {}
        print(f'{includes["users"][0]}: {self.tweet}, {includes["places"][0]["full_name"]}\n')
        print(f'Tweets with location: {self.counts_dict["locations"]}')

    
    
