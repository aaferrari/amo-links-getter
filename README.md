Set of script to obtain the links of the available addons in https://addons.mozilla.org and https://addons.thunderbird.net to facilitate backup jobs.
It currently get the following urls from the Android, Firefox, Thunderbird and Seamonkey addons:

* Information page.
* Reviews (only the pages, not the individual review).
* Images (preview), CSS and JS.
* The .xpi files of all the versions.
* User page.

The following table shows the links that are avoided or modified because they are considered redundant or unnecessary:

| Type              | Example                                                                                | Operation                                                  |
|-------------------|----------------------------------------------------------------------------------------|------------------------------------------------------------|
| [src param](https://addons-server.readthedocs.io/en/latest/topics/api/download_sources.html)         | addons.mozilla.org/en-US/firefox/addon/someaddon/?src=cb-dl-name               | Remove parameter                                           |
| Individual review | addons.mozilla.org/en-US/firefox/addon/someaddon/reviews/34368935              | Skip (reviews are grouped in */reviews/?page=**) |
| User reviews      | addons.mozilla.org/en-US/firefox/addon/someaddon/reviews/user:3626             | Skip (the same as above)                         |
| Add review        | addons.mozilla.org/en-US/firefox/addon/someaddon/reviews/add                   | Skip (unnecessary)                                      |
| type:attachment   | addons.mozilla.org/firefox/downloads/file/609267/type:attachment/someaddon.xpi | Skip (redundant)                                       |
| RSS               | addons.mozilla.org/en-US/firefox/addon/someaddon/reviews/format:rss            | Skip (unnecessary)                                      |
| # link            | addons.mozilla.org/en-US/firefox/addon/someaddon#something                     | Remove #*                                                 |

Requirements
------------
* [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/)
* requests
* [sqlite3 command](https://sqlite.org/download.html)
* Only tested in Python 2 but in Python 3 should work.

Usage
-----
1. Copy results-example.json to results.json.
2. Create url-crc.sqlite database with this command: `sqlite3 url-crc.sqlite < url-crc.sql`
3. Run addonlister.py to get the main page of each extension.
4. Once the previous script finishes running, run urlgetter.py.
5. When urlgetter.py finishes traversing all the addons pages, it is possible to save to a file a list with all the links obtained through the following command:
`sqlite3 url-crc.sqlite "select url from url_crc where (url like '%addons.cdn.mozilla.net/%' or url like '%addons.mozilla.org/%' or url like '%addons.thunderbird.net/%') and url not like '%outgoing.prod.mozaws.net%';" > url-list.txt`