from bs4 import BeautifulSoup
import re, requests, json, sqlite3
from time import time
from binascii import crc32
from urllib import quote
from urlparse import urlparse

# TODO: Add requests.exceptions.ConnectionError try-catch

link_detector = re.compile(".*/((android|firefox|thunderbird|seamonkey)/(addon|user|collections|downloads|extensions)|user-media|static/(js|css|img))|versions|reviews/.*")
# To avoid saving redundant or unnecessary links
avoid_crawling = re.compile(".*/(reviews/([0-9]+|add|user:[^/]+)|type:attachment|format:rss)(/|$).*")

# Add item to pending list with some fixes
def aggregator(item):
    cleaned = re.sub("/?\?src=.+|/$", "", item)
    if cleaned.startswith("/") == True: cleaned = domain + cleaned
    try: cleaned_hash = crc32(cleaned)
    # Managing unicode urls
    except UnicodeEncodeError: cleaned_hash = crc32(quote(cleaned.encode("utf8")))
    if cleaned_hash not in results["pending"]:
        results["pending"].append(cleaned_hash)
        #if cur_db.execute("select crc32 from url_crc where crc32= %i" % cleaned_hash).fetchone() == None:
        cur_db.execute("insert or ignore into url_crc values('%s', %i, '%s')" % (cleaned, cleaned_hash, url))
        #url_db.commit()

def get_links(soup):
    for a in soup.findAll("a", {"href": link_detector}): aggregator(a["href"])

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
