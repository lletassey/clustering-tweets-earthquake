"""Utility functions for interacting with Tweepy objects."""
from geopy import OpenMapQuest
import keys
import time 

def get_tweet_content(tweet, location=False):
    """Return dictionary with data from tweet (a Status object)."""
    fields = {}
    fields['screen_name'] = tweet.user.screen_name

    # get the tweet's text
    try:  
        fields['text'] = tweet.extended_tweet.full_text
    except: 
        fields['text'] = tweet.text

    if location:
        fields['location'] = tweet.user.location

    return fields

def get_geocodes(tweet_list):
    """Get the latitude and longitude for each tweet's location.
    Returns the number of tweets with invalid location data."""
    print('Getting coordinates for tweet locations...')
    geo = OpenMapQuest(api_key=keys.mapquest_key)  # geocoder
    bad_locations = 0  

    for tweet in tweet_list:
        processed = False
        delay = .1  # used if OpenMapQuest times out to delay next call
        while not processed:
            try:  # get coordinates for tweet['location']
                geo_location = geo.geocode(tweet['location'])
                processed = True
            except:  # timed out, so wait before trying again
                print('OpenMapQuest service timed out. Waiting.')
                time.sleep(delay)
                delay += .1

        if geo_location:  
            tweet['latitude'] = geo_location.latitude
            tweet['longitude'] = geo_location.longitude
        else:  
            bad_locations += 1  # tweet['location'] was invalid
    
    print('Done geocoding')
    return bad_locations
