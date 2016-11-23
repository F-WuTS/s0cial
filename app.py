from Meh import Config, Option, ExceptionInConfigError
from facepy import GraphAPI
import tweepy
from time import sleep

CONFIG_PATH = "config.cfg"

config = Config()
config += Option("twitter_accounts", ("robot0nfire", "team_items"),
	validator=lambda x: type(x) in (tuple, list), comment="Twitter accounts")
config += Option("twitter_consumer_token", "", comment="Twitter consumer token")
config += Option("twitter_consumer_secret", "", comment="Twitter consumer secret")
config += Option("twitter_access_token", "", comment="Twitter access token")
config += Option("twitter_access_token_secret", "", comment="Twitter access token secret")
config += Option("poll_rate", 60, comment="Twitter access token secret")
config += Option("facebook_oauth", "", comment="Facebook Graph API token")

try:
	config = config.load(CONFIG_PATH)
except (IOError, ExceptionInConfigError):
	config.dump(CONFIG_PATH)
	config = config.load(CONFIG_PATH)


auth = tweepy.OAuthHandler(config.twitter_consumer_token, config.twitter_consumer_secret)
auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)

api = tweepy.API(auth)

twitter_users = []
for user in config.twitter_accounts:
	twitter_users.append(api.get_user(user))

last_ids = {}
for user in twitter_users:
	last_ids[user] = user.timeline()[0].id

try:
	while True:
		to_retweet = []
		for user in twitter_users:
			tweets_ = user.timeline(since_id=last_ids[user])
			tweets = []
			for tweet in tweets_:
				if "#robot4you" in tweet.text or "#r4y" in tweet.text:
					tweets.append(tweet)
			if len(tweets) > 0:
				print("New tweets by '%s'" % user.name)
				last_ids[user] = tweets[0].id
			for tweet in tweets:
				print(tweet.text)
				to_retweet.append(tweet.id)
		for tweet_id in to_retweet:
			api.retweet(tweet_id)
		sleep(config.poll_rate)
except KeyboardInterrupt:
	pass