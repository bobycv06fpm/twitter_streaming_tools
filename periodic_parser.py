# Preparation
import json, logging, re, csv
import configparser
from datetime import date, timedelta
from collections import Counter, OrderedDict
from operator import itemgetter
from nltk.corpus import stopwords 
import os.path

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

# Flatten texts; subset should be False or a list of text strings
def totextlist(texts, subset = False):
	if subset != False:
		texts = [words for words in texts if not set(words).isdisjoint(subset)]
	textlist = [word for words in texts for word in words]
	return textlist

# Normalize frequency of one text list by another
def normalize_counts(adjust, base, threshold, top = False):
	if isinstance(adjust, list):
		adjust = Counter(adjust)
	if isinstance(base, list):
		base = Counter(base)

	adjusted = dict()
	for s in adjust:
		if adjust[s] > threshold:
			if base[s] == 0:
				base[s] = 1
			adjusted[s] = adjust[s]/base[s]
	
	adjusted = sorted(adjusted.items(), key = itemgetter(1), reverse = True)
	if top != False:
		adjusted = adjusted[0:top]
	return adjusted

# Writing the updated list of words to csv
def updatecsv(wordlist, file = PARAMS['DEFAULT']['updated_wordlist']):
	if not os.path.isfile(file):
		with open(file, 'a', encoding = 'utf-8', newline = '') as out_file:
			writer = csv.writer(out_file)
			writer.writerow(['string', 'score', 'date'])
	datelabel = getdate()
	with open(file, 'a', encoding = 'utf-8', newline = '') as out_file:
		writer = csv.writer(out_file)
		for row in wordlist:
			writer.writerow(row + (datelabel,))

# Updating parameters file
def paramsout(new_track, config = 'config.ini'):
	# Read in config file again
	PARAMS = configparser.ConfigParser()
	PARAMS.read(config)
	
	datelabel = getdate()
	spaced_comma = ', '
	
	# Format new tracks and combine with base tracks
	new_track = [x[0] for x in new_track]
	track_base = PARAMS['filter']['track_base'].split(spaced_comma)
	new_track.extend(track_base)
	new_track = list(set(new_track))
	new_track = spaced_comma.join(new_track)	
	
	# Updating output files
	output = 'tweets_' + datelabel + '.txt'
	log = 'streamlog_' + datelabel + '.log'
	
	# Rewriting config file
	PARAMS['filter']['track'] = new_track
	PARAMS['DEFAULT']['rawjson'] = output
	PARAMS['DEFAULT']['streamlog'] = log
	
	with open('config_test.ini', 'w') as configfile:
		PARAMS.write(configfile)

#