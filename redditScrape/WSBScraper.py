import praw
import csv
import re
import json
import requests

reddit = praw.Reddit()

class StockTrade(object):
    def __init__(self, postID, postURL, ups, downs, numComments, stock):
        self.postID = postID
        self.url = postURL
        self.stock = stock
        self.ups = ups
        self.downs = downs
        self.numComments = numComments

    def jsonEnc(self):
        return{"stock":self.stock,"postID":self.postID,"postURL":self.url,"ups":self.ups,"downs":self.downs,"numComments":self.numComments}

def jsonDefEncoder(obj):
    if hasattr(obj, "jsonEnc"):
        return obj.jsonEnc()
    else:
        return obj.__dict__

class SubredditScraper:
    def __init__(self,sub,sort="new", lim=900):
        self.sub = sub
        self.sort = sort
        self.lim = lim

        print(
            'SubredditScraper instance created with values '
            f'sub = {sub}, sort = {sort}, lim = {lim}'
            )

    def set_sort(self):
        if self.sort == 'new':
            return self.sort, reddit.subreddit(self.sub).new(limit=self.lim)
        elif self.sort == 'top':
            return self.sort, reddit.subreddit(self.sub).top(limit=self.lim)
        elif self.sort == 'hot':
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)
        else:
            self.sort = 'hot'
            print('Sort method was not found, default is hot')
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)

    def get_posts(self):

        stockTickers = {}
        with open('tickers.csv', mode='r') as infile:
            reader = csv.reader(infile)
            for row in reader:
                stockTickers[row[0].split(',')[0]] = {}

        sort, subreddit = self.set_sort()

        print(f'Collecting information from r/{self.sub}')
        mentionedStocks = []
        i = 0
        # print(mentionedStocks)
        for post in subreddit:
            i = i + 1
            print(i)
            if post.link_flair_text != 'Meme':
                for stock in stockTickers.keys():
                    if(re.search(r'\s+\$?' + stock + r'\$?\s+', post.selftext) or re.search(r'\s+\$?' + stock + r'\$?\s+', post.title)):
                        stockTickers[stock][post.id] = StockTrade(post.id, post.permalink, post.ups, post.downs, post.num_comments, stock)
        for stock in stockTickers:
            if (len(stockTickers[stock]) > 0):
                for post in stockTickers[stock]:
                    mentionedStocks.append(stockTickers[stock][post])
        json_object = json.dumps(mentionedStocks, default=jsonDefEncoder, indent = 3)
        # print(json_object)
        # print(type(json_object))
        formatJson = json.loads(json_object)
        # print(formatJson)
        # print(type(formatJson))
        for items in formatJson:
            print(items)
        headers = {"Content-type":"application/json", "Accept":"application/json"}
        r = requests.post("http://localhost:8000/api/stocks", data=formatJson, verify=False)
        print(r.status_code)
        print(r.text)

if __name__ == '__main__':
    SubredditScraper('wallstreetbets', lim=15, sort='new').get_posts()
