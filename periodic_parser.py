# Preparation
import json, logging, re
import configparser
from datetime import date, timedelta
from collections import Counter
from nltk.corpus import stopwords 

PARAMS = configparser.ConfigParser()
PARAMS.read('config.ini')

# Setting up log file
logging.basicConfig(filename = PARAMS['DEFAULT']['parselog'], filemode = 'a', format = '(%(asctime)s) %(levelname)s: %(message)s', level = logging.INFO)

# Get Date
def getdate(offset = 0):
	today = date.today() + timedelta(days = offset)
	datelabel = today.strftime("%Y%m%d")
	return datelabel

# Read data from previous date
def file2text(infiles):
	texts = []
	i = 0
	with open(infiles, 'r', encoding = 'utf-8-sig') as read_file:
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
	puncs = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~‘’“”—'
	text = [word.strip(puncs) for word in text]
	return text	

# Cleaning texts
def cleantext(text, remove_stopwords = True):
	text = text.lower() # lower cases
	text = re.sub(r"http\S+", "", text) # remove http urls
	text = text.split() # split by whitespace
	text = removepuncs(text) # remove punctuations (but keep '#' and '@'; note that usernames ending in _ will be wrong)
	if remove_stopwords:
		stop_words = set(stopwords.words('english'))
		stop_words.add('') # adding '' to be removed because it is introduced by removepuncs()
		text = [word for word in text if word not in stop_words] # remove stopwords
	else:
		text = [word for word in text if word != '']
	return text

# Flatten texts
def totextlist(texts, subset = False):
	if subset != False:
		texts = [words for words in texts if not set(words).isdisjoint(subset)]
	textlist = [word for words in texts for word in words]
	return textlist

# Count word frequencies



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