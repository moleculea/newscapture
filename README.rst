newscapture for MediaWiki
=========================
Sync news titles from an external news website to a specific template page on your MediaWiki site.

Applicability
_____________
* MediaWiki site which is routinely maintained with `Pywikipediabot <http://www.mediawiki.org/wiki/Manual:Pywikipediabot>`_
* External news site which does not provide RSS feed, but has only index pages of news titles and links (URLs are ID-incremented)

Prerequisite
____________
* `Pywikipediabot <http://www.mediawiki.org/wiki/Manual:Pywikipediabot>`_
* An authorized bot account on your MediaWiki to be associated with Pywikipediabot

Features
--------
* Capture news from the specified site and dump into TXT files (can be imported to MediaWiki site using Pywikipediabot)
* Parse news contents and provide internal links of matched existing pages on your MediaWiki sites 
* Provide both unreferenced news and referenced news
* Configure number of news to capture each time
* Configure filtering rules

Usage
_____

1. Configuration: edit conf.py;
2. Script configuration (optional): edit sample sync.sh or write your own script;
3. Test:

.. code-block:: bash

    $ python main.py

See if the following files are created in <FILE_DIR>:

.. code-block:: bash

    flag
    news_append.txt
    news.id
    news_ref.txt
    news_unref.txt

* **flag** (optinal): use with the sample sync.sh script; indicates whether there is NEW news each time you execute main.py

* **news.id**: stores the ID of the last synced news (largest)

* **news_append.txt**: stores NEW news which differed from the last sync. This is useful for you to collect news to a single list page on your MediaWiki site. Use the following Pywikipedia command to upload (append) this file:

.. code-block:: bash

	$ python /path/to/pywikipedia/add_text.py -textfile:/path/to/<FILE_DIR>/news_append.txt -page:<WIKI_PAGE> -bottom -always

* **news_ref.txt**: news with reference links. This file has the following format:

::
	
	AAAA<!-- automatically created content  by Foobar-Bot 2013-03-16 14:00:02-->TTTT<Template:NewsPage>TTTT

	News contents ...

	BBBB

Use the following Pywikipedia command to upload this file to your MediaWiki site: 

.. code-block:: bash

	$ python /path/to/pywikipedia/pagefromfile.py -start:AAAA -end:BBBB -titlestart:TTTT -titleend:TTTT -file:/path/to/news_ref.txt

* **news_unref.txt**: news with no reference links. The Pywikipedia command to upload this file is similar to that of news_ref.txt

4. Deploy: use cron to periodically run your customized shell script.

License
_______

BSD License
