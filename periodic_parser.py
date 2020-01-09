# Preparation
import json
from datetime import date, timedelta
from collections import Counter

PARAMS = {}

with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')

# Get Date
def getdate(offset = 0):
	today = date.today() + timedelta(days = offset)
	datelabel = today.strftime("%Y%m%d")
	return datelabel

# Read data from previous date
def file2text():
	texts = []
	i = 0
	with open(PARAMS['output'][0], 'r', encoding = 'utf-8-sig') as read_file:
		for x in read_file:
			i += 1
			try:
				data = json.loads(x)
				if 'user' in data and 'retweeted_status' not in data:
					text = parsetweet(data)
					text_cleaned = cleantext(text)
					
					texts.append(text_cleaned)
			except Exception as e: 
				logging.exception('Error in entry:' + str(i))
	return texts
	
# Parse data for words
def parsetweet(tweet):
	if tweet['truncated']:
		text = tweet['extended_tweet']['full_text']
	else:
		text = tweet['text']
	return text

# remove punctuations
def removepuncs(text):
	puncs = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~‘’'
	text = [word.strip(puncs) for word in text]
	return text	
	
# Cleaning texts
def cleantext(text):
	text = text.lower() # lower cases
	text = re.sub(r"http\S+", "", text) # remove http urls
	text = text.split() # split by whitespace
	text = removepuncs(text) # remove punctuations (but keep '#' and '@'; note that usernames ending in _ will be wrong)
	text = [word for word in removepuncs(text) if word != ''] # remove '' (introduced by removepuncs)
	return text

# Clean and flatten texts
def totextlist(texts, subset = False):
	cleaned = [cleantext(text) for text in texts]
	if subset != False:
		cleaned = [words for words in cleaned if not set(words).isdisjoint(subset)]
	textlist = [word for words in cleaned for word in words]
	return textlist



# Normalize counts
#def normalizecounts():
#	f
	
# Return list of words
	
# Writing parameters file
def paramsout(track, follow):
	datelabel = getdate()
	semicolon = ';'
	output = 'output:tweets_' + datelabel + '.txt\n'
	log = 'log:log_' + datelabel + '.log\n'
	tracks = 'track:' + semicolon.join(track) + '\n'
	follows = 'follow:' + semicolon.join(follow)
	with open('params.txt', 'w', encoding = 'utf-8', newline = '') as outfile:
		outfile.writelines([output, log, tracks, follows])

#