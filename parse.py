import os, json, csv, logging

# Parameters
PARAMS = {}

with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')

# Defining functions
# Function to recursively extract value with 'key' in the json 'obj'
# Adapted from https://hackersandslackers.com/extract-data-from-complex-json-python/
def extract_values(obj, key):
	arr = []

	def extract(obj, arr, key):
		if isinstance(obj, dict):
			for k, v in obj.items():
				if isinstance(v, (dict, list)):
					extract(v, arr, key)
				if k == key:
					if isinstance(v, list):
						arr.extend(v)
					if isinstance(v, str):
						arr.append(v)
		elif isinstance(obj, list):
			for item in obj:
				extract(item, arr, key)
		return arr

	results = extract(obj, arr, key)
	return results

# Function to parse twitter json object then write out
def write_data(path, data):
	# Get unique hashtags
	ht = extract_values(data, 'hashtags')
	if len(ht) > 0:
		ht = [x['text'] for x in ht]
		ht = set(ht)
		ht = list(ht)
	ht = str(ht)[1:-1]

	# Check if 'greta' or 'thunberg' is in the tweet at all
	data_string = json.dumps(data).lower()
	if 'greta' in data_string or 'thunberg' in data_string:
		gt = '1'
	else:
		gt = '0'

	# Getting retweet data
	if 'retweeted_status' in data:
		rt_id = data['retweeted_status']['id_str']
		rt_time = data['retweeted_status']['created_at']
		rt_user = data['retweeted_status']['user']['id_str']
		rt_loc = data['retweeted_status']['user']['location']
	else:
		rt_id = ''
		rt_time = ''
		rt_user = ''
		rt_loc = ''
		
	# Writing data
	with open(path, 'a', encoding = 'utf-8', newline = '') as out_file:
		writer = csv.writer(out_file)
		writer.writerow([data['id_str'],
						 data['created_at'],
						 data['user']['id_str'],
						 data['user']['location'],
						 rt_id,
						 rt_time,
						 rt_user,
						 rt_loc,
						 ht,
						 gt
						])

# Function to start the csv file with the proper header
def start_file(path):
	with open(path, 'w', encoding = 'utf-8', newline = '') as out_file:
		csv.writer(out_file).writerow(['status_id', 'status_time', 'user_id', 'user_location', 'rt_id', 'rt_time', 'rt_user', 'rt_location', 'hashtags', 'gt'])

# Preparing files
start_file('eng_out.txt')
start_file('fin_out.txt')
start_file('swe_out.txt')
start_file('all_out.txt')
logging.basicConfig(filename = 'parser_log_file.log', filemode = 'a', format = '(%(asctime)s) %(levelname)s: %(message)s', level = logging.INFO)

# Looping through all days and all tweets
n_tweet = 0
n_fin = 0
n_eng = 0
n_swe = 0
with open(PARAMS['output'][0], 'r', encoding = 'utf-8-sig') as read_file:
	for x in read_file:
		try:
			data = json.loads(x)
			if 'user' not in data:
				with open('stream_notices.txt', 'a', encoding = 'utf-8') as checker: checker.write(json.dumps(data) + '\n')
			else:
				write_data('all_out.txt', data)
				n_tweet += 1
				lang = extract_values(data, 'lang')
				if 'fi' in lang:
					write_data('fin_out.txt', data)
					n_fin += 1
				if 'en' in lang:
					write_data('eng_out.txt', data)
					n_eng += 1
				if 'sv' in lang:
					write_data('swe_out.txt', data)
					n_swe += 1
		except Exception as e: 
			logging.exception('Error.')
			
		if n_tweet % 100000 == 0:
			logging.info('Parsed ' + str(n_tweet) + ' tweets.')
			print('Parsed ' + str(n_tweet) + ' tweets.')			

logging.info("Finished. Processed: " + str(n_tweet) + " tweets. (English: " + str(n_eng) + "; Finnish: " + str(n_fin) + "; Swedish: " + str(n_swe) + '.)')		
print("Finished. Processed: " + str(n_tweet) + " tweets. (English: " + str(n_eng) + "; Finnish: " + str(n_fin) + "; Swedish: " + str(n_swe) + '.)')

