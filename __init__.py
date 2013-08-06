import nltk   
from nltk.probability import FreqDist
import urllib2
from urllib import urlopen
import simplejson;

from flask import Flask
from twython import Twython, TwythonError

from flask.ext.cache import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.debug = True

#Word count method
def doWordCount(w):
	url = "http://news.bbc.co.uk/2/hi/health/2284783.stm"    
	html = urlopen(url).read()    
	raw = nltk.clean_html(html)  

	words = nltk.tokenize.word_tokenize(raw)

	fd = FreqDist(words)

	return fd[w]


@app.route("/")
def hello():
   return ("Currently available APIS: \n \n /wordcount/WORD")


@app.route("/wordcount/<word>")
def countIt(word):
   wc = doWordCount(word)
   print word
   return simplejson.dumps({'word':word, 'count':wc})

@app.route("/drones/laststrike")
def lastStrike():
	req = urllib2.Request("http://api.dronestre.am/data")
	opener = urllib2.build_opener()
	f = opener.open(req)
	strikes = simplejson.load(f).get("strike")
	lastStrike =  strikes[len(strikes) - 1];
	out =  simplejson.dumps(lastStrike, sort_keys=True, indent=4 * ' ')
	return out

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
