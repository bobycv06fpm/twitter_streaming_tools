# Preparation
from datetime import date

# Get Date
def getdate():
	today = date.today()
	datelabel = today.strftime("%d%m%Y")
	return datelabel

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

