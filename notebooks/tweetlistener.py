import tweepy

class TweetListener(tweepy.StreamingClient):
    """Handles incoming Tweet stream."""

    def __init__(self, bearer_token, counts_dict, tweets_list, topic):
        """Configure the TweetListener."""
        self.tweets_list = tweets_list
        self.counts_dict = counts_dict
        self.topic = topic
        self.tweet = ''
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

    def on_includes(self, includes):
        """Called when a new includes object arrives."""
        if not includes.get('places'):
            return
        self.counts_dict['locations'] += 1
        self.tweets_list.append(self.tweet)
        print(f'{includes["users"][0]}: {self.tweets_list[-1]}, {includes["places"][0]["full_name"]}\n')
        print(f'Tweets with location: {self.counts_dict["locations"]}')

    
    
