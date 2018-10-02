from bs4 import BeautifulSoup
import re, requests, json, sqlite3
from time import time
from binascii import crc32
from urllib import quote
from urlparse import urlparse

# TODO: Add requests.exceptions.ConnectionError try-catch

link_detector = re.compile(".*/((android|firefox|thunderbird|seamonkey)/(addon|user|collections|downloads|extensions)|user-media|static/(js|css|img))|versions|reviews/.*")
# To avoid saving redundant or unnecessary links
avoid_crawling = re.compile(".*/(reviews/([0-9]+|add|user:[^/]+)|format:rss)(/|$).*")
# Removes unnecessary characters/parameters of a url
cleaner = re.compile("(/?\?src=.+|/|/?\)|/?#.+)$")
# From https://github.com/mozilla/addons-server/blob/master/src/olympia/constants/search.py
lang_codes = re.compile("/(he|da|bg|sl|uk|hu|pt(-(pt|br))?|cs|en(-(us|ca|gb))?|id|fr|ca|fa|nl|sk|es|ru|pl|ar|eu|ja|ko|sq|fi|el|ro|mn|de|sv(-se)?|af|zh(-(cn|tw))?|vi|it)/", re.I)

def get_hash(text):
    try: crc_hash = crc32(text)
    # Managing unicode urls
    except UnicodeEncodeError: crc_hash = crc32(quote(text.encode("utf8")))
    return crc_hash

# Add item to pending list with some fixes
def aggregator(item):
    cleaned = cleaner.sub("", item).replace("http://", "https://")
    cleaned = lang_codes.sub("/en-US/", cleaned)
    if cleaned.startswith("/") == True: cleaned = domain + cleaned
    # Skip links with type:attachment only if the same link without this segment
    # has been discovered before
    if get_hash(cleaned.replace("/type:attachment", "")) in results["pending"]: return
    cleaned_hash = get_hash(cleaned)
    if cleaned_hash not in results["pending"] and avoid_crawling.match(cleaned) == None:
        results["pending"].append(cleaned_hash)
        #if cur_db.execute("select crc32 from url_crc where crc32= %i" % cleaned_hash).fetchone() == None:
        cur_db.execute("insert or ignore into url_crc values('%s', %i, '%s')" % (cleaned, cleaned_hash, url))
        #url_db.commit()

url_sources = {"a": "href", "link": "href", "img": "src", "script": "src"}

def get_links(soup):
    tags = soup.select("a, img, link, script")
    for tag in tags: 
        url_tag = tag[url_sources[tag.__dict__["name"]]]
        if link_detector.match(url_tag) != None: aggregator(url_tag)

url_db = sqlite3.connect("url-crc.sqlite")
cur_db = url_db.cursor()
selector = [url[0] for url in cur_db.execute("select url from addons where checked <> 1")]
results = json.loads(file("results.json", "r").read())
interval = 300
last_time = time()
domain = ""

for url in selector:
    if time() >= last_time + interval:
        output = file("results.json", "w")
        output.write(json.dumps(results, indent=4, separators=(',', ': ')))
        output.close()
        url_db.commit()
        last_time = time()
    domain = "://".join(urlparse(url)[0:2])
    request = requests.get(url, cookies={"mamo":"off"})
    print "%s" % (url)
    if request.ok == True:
        soup = BeautifulSoup(request.text, 'html.parser')
        get_links(soup)
        for link in [url+"/versions", url+"/reviews"]:
            if avoid_crawling.match(link) != None: continue
            soup = BeautifulSoup(requests.get(link, cookies={"mamo":"off"}).text, 'html.parser')
            get_links(soup)
            # Detect next pages in page
            for match in soup.select("p.rel > a.jump"):
                try: url2, last_page = re.match("(.+)\?page=([0-9]+)$", match["href"]).groups()
                except AttributeError: continue
                for page in xrange(2, int(last_page)):
                    next_page = "%s?page=%i" % (url2, page)
                    soup2 = BeautifulSoup(requests.get(domain + next_page, cookies={"mamo":"off"}).text, 'html.parser')
                    get_links(soup2)
                    aggregator(next_page)
    else: results["failed"][url]= request.status_code
    results["last"]=url
    foo =cur_db.execute("update addons set checked=1 where url='%s'" % url)
    #url_db.commit()
