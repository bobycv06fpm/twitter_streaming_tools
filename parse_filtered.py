# Preparation
from periodic_parser import *
import logging, configparser

# Reading in configuation
PARAMS = configparser.ConfigParser()
PARAMS.read('config.ini')

# Setting up log file
logging.basicConfig(filename = PARAMS['filter']['parselog'], filemode = 'a', format = '(%(asctime)s) %(levelname)s: %(message)s', level = logging.INFO)

# Loading and parsing raw json file
tweets = file2text(infiles = PARAMS['filter']['rawjson'])

# Flattening tweets to text
textlist = totextlist(texts = tweets, subset = False)

# Obtain normalized counts
base_counts = count_in(infile = PARAMS['sample']['freq_dict'])
counts = normalize_counts(adjust = textlist, base = base_counts, threshold = 25, top = 400)

# Outputting updated word list and updating config file
updatecsv(counts, outfile = PARAMS['filter']['updated_wordlist'])
updateconfig_filter(counts, offset = 1, old_config = 'config.ini')
