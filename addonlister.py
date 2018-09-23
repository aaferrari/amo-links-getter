from bs4 import BeautifulSoup
import re, requests, sqlite3
from urlparse import urlparse

# Get addons urls and add these to database with some fixes
def aggregator(item):
    for tag in soup.select('.items > .addon > .info > h3 > a'):
        cleaned = re.sub("/?\?src=.+|/$", "", tag["href"])
        if cleaned.startswith("/") == True: cleaned = domain + cleaned
        if cleaned.find("/addon/") != -1: #print(cleaned)
            cur_db.execute("insert or ignore into addons values('%s', 0)" % cleaned)

def get_pages(soup):
    pages =[]
    for match in soup.select("p.rel > a.jump"):
        try: url, last_page = re.match("(.+)[&\?]page=([0-9]+)$", match["href"]).groups()
        except AttributeError: continue
        for page in xrange(2, int(last_page)): pages.append("%s%s&page=%i" % (domain, url, page))
    return pages

url_db = sqlite3.connect("url-crc.sqlite")
cur_db = url_db.cursor()
repositories = ["https://addons.mozilla.org/android/extensions/?sort=name",
"https://addons.mozilla.org/firefox/extensions/?sort=name",
"https://addons.thunderbird.net/seamonkey/extensions/?sort=name",
"https://addons.thunderbird.net/thunderbird/extensions/?sort=name"]

for repository in repositories:
    domain = "://".join(urlparse(repository)[0:2])
    soup = BeautifulSoup(requests.get(repository, cookies={"mamo":"off"}).text, 'html.parser')
    pending = get_pages(soup)
    aggregator(soup)
    for link in pending:
        print(link)
        soup = BeautifulSoup(requests.get(link, cookies={"mamo":"off"}).text, 'html.parser')
        aggregator(soup)

url_db.commit()
url_db.close()