from periodic_parser import *
import logging, configparser

# Reading in configuration file
PARAMS = configparser.ConfigParser()
PARAMS.read('config.ini')