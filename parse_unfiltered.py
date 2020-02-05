# Preparation
from periodic_parser import *
import logging, configparser

# Reading in configuation
PARAMS = configparser.ConfigParser()
PARAMS.read('config.ini')

# Setting up log file
logging.basicConfig(filename = PARAMS['sample']['parselog'], filemode = 'a', format = '(%(asctime)s) %(levelname)s: %(message)s', level = logging.INFO)

# Loading and parsing raw json file
tweets = file2text(infiles = PARAMS['sample']['rawjson'])

# Flattening tweets to text
textlist = totextlist(texts = tweets, subset = False)

# Outputting frequency dict as .pickle
count_out(textlist, outfile = PARAMS['sample']['freq_dict'])

# Update config file
updateconfig_sample()
