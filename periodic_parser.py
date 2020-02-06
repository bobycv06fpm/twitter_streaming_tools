# Preparation
import json, re, csv, logging, pickle, configparser
import os.path
from datetime import date, timedelta
from collections import Counter, OrderedDict
from operator import itemgetter
from nltk.corpus import stopwords 

logger = logging.getLogger(__name__)

# Get Date
def getdate(offset = 0):
	today = date.today() + timedelta(days = offset)
	datelabel = today.strftime("%Y%m%d")
	return datelabel

# Read data from file
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
				logger.exception('Error in entry:' + str(i))
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

# Save counting dict as pickle
def count_out(textlist, outfile):
	textlist = Counter(textlist)
	with open(outfile, 'wb') as out_pickle:
		pickle.dump(textlist, out_pickle)

# Reading in freq dict
def count_in(infile):
	with open(infile, 'rb') as in_pickle:
		freq_dict = pickle.load(in_pickle)
	return freq_dict
	
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
def updatecsv(wordlist, outfile):
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
def updateconfig_filter(new_track, offset = 1, old_config = 'config.ini', new_config = None):
	if new_config == None:
		new_config = old_config
	# Read in config file again
	PARAMS = configparser.ConfigParser()
	PARAMS.read(old_config)
	
	datelabel = getdate(offset)
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
	PARAMS['filter']['rawjson'] = output
	PARAMS['filter']['streamlog'] = log
	
	with open(new_config, 'w') as configfile:
		PARAMS.write(configfile)

def updateconfig_sample(offset = 30, old_config = 'config.ini', new_config = None):
	if new_config == None:
		new_config = old_config
	# Read in config file again
	PARAMS = configparser.ConfigParser()
	PARAMS.read(old_config)
	
	datelabel = getdate(offset)
	output = 'unfiltered_' + datelabel + '.txt'
	
	PARAMS['sample']['rawjson'] = output
	
	with open(new_config, 'w') as configfile:
		PARAMS.write(configfile)