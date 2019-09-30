# Preparation
import os, time, logging
from tweepy import OAuthHandler, Stream, StreamListener, API

# Parameters and authentication
PARAMS = {}
CREDS = {}

with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')
		
with open('auth.txt', encoding = 'utf-8') as creds:
	for line in creds:
		creds, value = line.strip().split(':', 1)
		CREDS[creds] = value
        
OUTFILE = PARAMS['output'][0]

# Set up logging
logging.basicConfig(filename = PARAMS['log'][0], filemode = 'a', format = '(%(asctime)s) %(levelname)s: %(message)s', level = logging.INFO)

# Authentication
auth = OAuthHandler(CREDS['consumer_key'], CREDS['consumer_secret'])
auth.set_access_token(CREDS['access_token'], CREDS['access_token_secret'])
api = API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

# Defining listener
class Listener(StreamListener):
	# Actual tweet content
	def on_data(self, tweet):
		try:
			with open(OUTFILE, 'a', encoding='utf-8', newline = '') as outfile:
				outfile.write(tweet)

			global tweetNum
			tweetNum += 1
			if tweetNum % 1000 == 0:
				print(str(tweetNum) + " tweets collected.")
				logging.info(str(tweetNum) + " tweets collected.")
		except Exception as e:
			logging.exception("Exception occurred when writing data.")
		
		return True
	
	# Some sort of error
	def on_error(self, status_code):
		if status_code == 420:
			global last_420
			global err_420
			if time.time() - last_420 > 43200:
				err_420 = 0
			last_420 = time.time()
			stopsec = 60*(2**err_420)
			err_420 += 1
			print("Error 420. Pausing for " + str(stopsec) + " seconds before restarting.")
			logging.warning("Error 420. Pausing for " + str(stopsec) + " seconds before restarting.")
			time.sleep(stopsec)
		else:
			global last_err
			global err_other
			if time.time() - last_err > 7200:
				err_other = 0
			last_err = time.time()
			stopsec = 5*(2**err_other)
			if err_other < 6:
				err_other += 1
			print("Error " + str(status_code) + ". Pausing for " + str(stopsec) + " seconds before restarting.")
			logging.warning("Error " + str(status_code) + ". Pausing for " + str(stopsec) + " seconds before restarting.")
			time.sleep(stopsec)
		
		return True
    
    # Return disconnect message
	def on_disconnect(self, notice):
		global last_disc
		global disconnects
		if time.time() - last_disc > 7200:
			disconnects = 0
		last_disc = time.time()
		if disconnects < 16:
			disconnects += 0.25
		print("Stream disconnected: " + notice + " Waiting " + str(disconnects) + " seconds before restarting.")
		logging.exception("Stream disconnected: " + notice + " Waiting " + str(disconnects) + " seconds before restarting.")
		time.sleep(disconnects)
		return True
    
    # Print warnings
	def on_warning(self, notice):
		print("Warning: " + notice)
		logging.warning("Warning: " + notice)
		return True

# Starting streaming
listener = Listener()
streamer = Stream(auth = api.auth, listener = listener)

tweetNum = 0
err_420 = 0
err_other = 0
disconnects = 0
last_420 = time.time() - 43200
last_err = time.time() - 7200
last_disc = time.time() - 7200


def recursive_streaming(tags):
	try:
		print('Start streaming.')
		logging.info('Start streaming with filters: ' + str(PARAMS['track']))
		streamer.filter(follow = None, track = tags, encoding = 'utf8', filter_level = None, stall_warnings = True)
	except KeyboardInterrupt:
		print('Manually stopped. ' + str(tweetNum) + ' tweets collected.')
		logging.info('Manually stopped. ' + str(tweetNum) + ' tweets collected.')
		streamer.disconnect()
	except Exception as e:
		global last_disc
		global disconnects
		if time.time() - last_disc > 7200:
			disconnects = 0
		last_disc = time.time()
		if disconnects < 16:
			disconnects += 0.25
		print("Stream stopped. Waiting " + str(disconnects) + " seconds before restarting.")
		logging.exception("Stream stopped. Waiting " + str(disconnects) + " seconds before restarting.")
		time.sleep(disconnects)
		recursive_streaming(tags)

recursive_streaming(tags = PARAMS['track'])
