Set of script to obtain the links of the available addons in https://addons.mozilla.org and https://addons.thunderbird.net to facilitate backup jobs.
It currently get the following urls from the Android, Firefox, Thunderbird and Seamonkey addons:

* Information page.
* Reviews (only the pages, not the individual review).
* Images (preview), CSS and JS.
* The .xpi files of all the versions.
* User page

Usage
-----

1. Copy results-example.json to results.json.
2. Create url-crc.sqlite database with this command: `sqlite3 url-crc.sqlite < url-crc.sql`
3. Run addonlister.py to get the main page of each extension.
4. Once the previous script finishes running, run urlgetter.py.