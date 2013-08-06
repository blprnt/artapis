#------------------------------------------------------------
# August 6, 2013
# These files are a VERY SIMPLE build of an API system in Flask, made for a demo in this post:
# http://blog.blprnt.com/blog/blprnt/the-api-as-art-object
#------------------------------------------------------------
#
# To actually run these files (you probably don't want to), you'll need Flask, as well as NLTK & Twython
#
# Oh, and FlaskCache.
#
# -Jer
#
#
#
#
#
#


import nltk   
from nltk.probability import FreqDist
import urllib2
from urllib import urlopen
import simplejson;

from flask import Flask
from twython import Twython, TwythonError

from flask.ext.cache import Cache

#Set up cache as to limit the calls to the Twitter API.
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.debug = True

#Word count method
def doWordCount(w):
	url = " http://blog.blprnt.com/blog/blprnt/the-api-as-art-object"    
	html = urlopen(url).read()    
	raw = nltk.clean_html(html)  

	words = nltk.tokenize.word_tokenize(raw)

	fd = FreqDist(words)

	return fd[w]


#This is a message that gets sent to anyone hitting the main api.blprnt.com url.
@app.route("/")
def hello():
   return ("<html><head><title>Look! Some APIs!</title></head><body>Currently available APIs: <ul><li>/wordcount/WORD</li><li>/drones/laststrikg</li><li>/dronetwitter/USER</li></ul></body></html>")

#Wordcount endpoint
@app.route("/wordcount/<word>")
def countIt(word):
   wc = doWordCount(word)
   print word
   return simplejson.dumps({'word':word, 'count':wc})

#Last Drone Strike endpoint
@app.route("/drones/laststrike")
def lastStrike():
	req = urllib2.Request("http://api.dronestre.am/data")
	opener = urllib2.build_opener()
	f = opener.open(req)
	strikes = simplejson.load(f).get("strike")
	lastStrike =  strikes[len(strikes) - 1];
	out =  simplejson.dumps(lastStrike, sort_keys=True, indent=4 * ' ')
	return out

#Twitter user - drone strike endpoint
@cache.cached(timeout=100)
@app.route("/dronetwitter/<username>")
def twitter(username):
	
	out = {'success':False};
	APP_KEY = "YOUR KEY HERE"
	APP_SECRET= "YOUR SECRET HERE"
	OAUTH_TOKEN = "YOUR TOKEN HERE"
	OAUTH_TOKEN_SECRET = "YOUR TOKEN SECRET HERE"
	# Requires Authentication as of Twitter API v1.1
	twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	try:
		user_timeline = twitter.get_user_timeline(screen_name=username)
		followers = twitter.get_followers_list(screen_name = username)
		out['victims'] = [];
		out['success'] = True
		for follower_id in followers["users"]:
			try:
				out['victims'].append({'name':follower_id["name"], 'lastWords':follower_id["status"]["text"]})
			except KeyError:
				print "bad twitter user. bad."

	except TwythonError as e:
		print e

	#print user_timeline
	txt = simplejson.dumps(out, indent=4 * ' ')
	return txt

if __name__ == "__main__":
    app.run()
