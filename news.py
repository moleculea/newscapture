# -*- coding: utf-8  -*-
import sys
import os
import re
import urllib2
import urlparse
import datetime
from conf import *
from newsprocess import *

class URL(object):
    """URL class: check validity of URLs upon initialization"""
    
    def __init__(self, url):
        """ Initialize URL
        
        @param url: List of strings or a single string representing URL(s)
        """
        self.url = []
        try:
            if isinstance(url, str):
                self.url = [url]

            if isinstance(url, list):
                self.url = url

        except:
            output.error("URL argument must be either of type string of list of strings.")
            sys.exit(1)
            
        self.info = []
        for u in self.url:
            self.info.append(URL._open(u))
                 
    @staticmethod
    def _open(url):
        """
        Try to open URL to check validity.
        Exit if cannot open URL.
        """
        r = None
        try:
            r = urllib2.urlopen(url)
            return r
        except:
            output.error("Cannot open URL: %s . Please double-check or retry later." % url)
            sys.exit(1)
    
    def getInfo(self, page):
        try:
            return self.info[page]
        except IndexError:
            output.error("Index is out range. It shoud be between 0 and %d", len(self.info) - 1)
            
    def __str__(self):
        urls = map(lambda u: urlparse.urlsplit(u).geturl(), self.url) 
        return "\n".join(urls)
        
class USTBNewsURL(URL):
    """
    USTBNewsURL: fetch a list of Article IDs USTB News site's URLs
    """
    def __init__(self, url, pattern, page=0, start_id=0, num=4):
        """ Initialize USTBNewsURL
        
        @param url: URLs (List) of the index pages that lists latest news
        @param pattern: regex pattern (raw string) to match Article IDs
        @param page: page number; indicates index of URL list in self.url
        @param start_id: starting Article ID (maximum, not included); 
                         default (0) means start from latest ID
        @param num: number of latest news to fetch for initial parsing 
        """
        super(USTBNewsURL, self).__init__(url)
        self.pattern = pattern
        self.page = page
        self.start_id = start_id
        self.num = num
        self.article_id = None # Full list of Article IDs (Integers)
        self.proper_id = None  # Proper list of Article IDs (Integers) after __parse() and getIDs()
        self.next_index = -1  # Index of the next consumed ID in self.article_id

    def __parse(self): 
        """Parse URL of index page using pattern to retrieve Article IDs"""
        source = decode(self.getInfo(self.page).read())
        rc = re.compile(self.pattern)
        id_list = rc.findall(source)
        self.article_id = sorted(map(int, list(set(id_list))), reverse=True) # Use set to remove duplicate items
        return self.article_id

    def getIDs(self):
        """Return a list of Article IDs by invoking __parse() method"""
        self.__parse() # Call __parse()
        start_index = 0
        
        if self.start_id == 0:
            self.proper_id = self.article_id[:self.num] # Update self.proper_id
            return self.proper_id
        
        else:
            try:
                start_id = int(self.start_id)
                start_index = self.article_id.index(start_id) + 1
                end_index = self.num + start_index
                self.proper_id = self.article_id[start_index:end_index] # Update self.proper_id
                if len(self.proper_id) < self.num:
                    output.warning("Insufficient IDs. Only %d IDs available from the succeeding ID to starting ID in the current page. Continue to next page..." % len(self.proper_id))
                    if len(self.url) < self.page + 2:
                        output.error("Insufficient URLs are provided. Checking stops.")
                        sys.exit(1)
                    else:                  
                        next_url = USTBNewsURL(self.url, self.pattern, self.page + 1, 0, self.num - len(self.proper_id))
                        self.proper_id = self.proper_id + next_url.getIDs()      # Update self.proper_id by concatenating two lists
                        self.article_id = self.article_id + next_url.getAllIDs() # Update self.article_id by concatenating two lists
                return self.proper_id
            
            except ValueError:
                output.warning("Subsequent ID to %d does not exist in the current page. Checking next page..." % self.start_id)
                if len(self.url) < self.page + 2:
                    output.error("Insufficient URLs are provided. Checking stops.")
                    sys.exit(1)
                else:
                    next_url = USTBNewsURL(self.url, self.pattern, self.page + 1, self.start_id, self.num)
                    self.proper_id = next_url.getIDs()
                    self.article_id = self.article_id + next_url.getAllIDs() # Update self.article_id by concatenating two lists
                    return self.proper_id

    def getLatestID(self):
        """
        Return (always) the latest (largest) ID in self.proper_id
        Must be called AFTER getIDs() is called
        """
        return sorted(self.proper_id, reverse=True)[0]
    
    def getAllIDs(self):
        """
        Return (all) Article IDs
        Must be called AFTER getIDs() is called
        """
        return self.article_id
    
    def getNextID(self):
        if self.next_index < 0:
            self.next_index = self.article_id.index(self.proper_id[self.num - 1]) + 1
        try:
            r = self.article_id[self.next_index]
            self.next_index += 1
            return r
        except IndexError:   # If out of range for self.article_id, return -1
            output.warning("Insufficient IDs in current Article IDs list. Checking next page...")
            if len(self.url) < self.page + 2:
                output.error("Insufficient URLs are provided. Checking stops.")
                sys.exit(1)
            else:                  
                next_url = USTBNewsURL(self.url, self.pattern, self.page + 1, 0, self.num - len(self.proper_id))
                next_url.getIDs()
                self.article_id = self.article_id + next_url.getAllIDs() # Update self.article_id by concatenating two lists
                return self.article_id[self.next_index]
            
    def __str__(self):
        """Return Article IDs separated by comma.
           If no Article ID is retrieved, simply return URL.
        """
        if self.article_id:
            return ", ".join(map(str, self.proper_id))
        else:
            return super(USTBNewsURL, self).__str__()

   
class Page(object):
    def __init__(self, url):
        """ Initialize Page 
        
        @param url: URL object with a single URL (List of a single string)
        """
        self.url = url
        self.info = url.info
        #print self.info[0].read()

        self.__source = decode(self.info[0].read())  # Decode read info (source text) into Unicode

            
        
    def getTitle(self):
        source = self.__source
        pattern = r"<title>(.+)</title>"
        m = re.search(pattern, source, re.DOTALL)
        return m.group(1).strip()
    
    def getSource(self):
        return self.__source
    
    def __str__(self):
        return self.url
        
class News(Page):
    """
    Represents a single piece of news
    """
    q_pattern = "" # Quasi-pattern shared among News object
    def __init__(self, id):
        page_url = News.IDtoURL(News.q_pattern, id)
        u = URL(page_url) # Instantiate URL object with converted URL string
        super(News, self).__init__(u)
        self.id = id
        self.wiki = ()
        
    @staticmethod
    def IDtoURL(q_pattern, id):
        """
        Convert "http://example.com/html/en%s.html" (Pattern) and 1234 (ID)
        To      "http://example.com/html/en1234.html"
        """
        return re.sub(r'%s', str(id), q_pattern)
        
    def getDate(self):
        try:
            return retrieveDate(self.getSource())
        except Exception, e:
            output.error("Error parsing date in news.\nNews ID: %d\nTitle: %s" % (self.id, self.getNews()))
            output.error(e)
            sys.exit(1)
    
    def getID(self):
        return self.id
        
    def getNews(self):
        return self.getTitle()
        
    def getURL(self):
        return self.url
    
    def setWiki(self, t):  # Set the filtered wiki text (2-tuple)
        self.wiki = t      # t: (wiki, wiki_unref)
    
    def getWiki(self, ref=False):
        if ref:
            return self.wiki[1]
        else:
            return self.wiki[0]
     
    def __str__(self):
        return "News ID: %d\nTitle: %s" % (self.id, self.getTitle())
    
class WikiNews(object):
    """
    Represent a list of valid News objects to be put on the designated wiki page
    """

    def __init__(self, dir, url, num, pattern, q_pattern, api_url, bot_tag="<!-- automatically created content by %s %s-->" %(BOT_NAME, datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")), templates=TEMPLATES):
        """
        @param dir: directory (absolute path, ending with slash /) of input (news.id) and output files
        @param url: URLs (List) of the index pages that lists latest news
        @param num: number of news to put
        @param pattern: regex pattern (raw string) to match Article IDs
        @param q_pattern: quasi-pattern
        @param api_url: URL of MediaWiki API (http://example.com/w/api.php)
        """

        self.url = URL(url)   # Auto check URLs upon initialization of URL
        self.raw_url = url    # Raw URL list
        self.dir = self.__checkDir(dir)
        self.num = num
        self.pattern = pattern
        self.q_pattern = q_pattern
        self.last_id = self.__readLastID() # Read news.id, -1 if news.id is empty
        self.latest_id = self.last_id # Latest ID at news page (whether news with this ID is valid or not)
        self.__flag = -1
        self.api_url = api_url
        self.ustb = USTBNewsURL(self.raw_url, pattern)
        self.wikinews = [] # List of news (News object) to put on MediaWiki site
        
        self.bot_tag = bot_tag
        
        
    def start(self):
        """
        Main sync process:
            Before start() is invoked:
                * Create URL object with "url" upon initialization of WikiNews
                * Instantiate USTBNewsURL
                * Read news.id as last_id in the "dir" directory 
            After start() is invoked:
                * Compare news.id with the latest proper_id of URL object 
                  to determine whether to continue sync
                * Instantiate USTBNewsURL, News objects
                * Check validity of News objects (and possibly reinstantiate USTBNewsURL)
                * Filter News objects
        """
        ustb = self.ustb
        init_ids = ustb.getIDs()
        latest_id = ustb.getLatestID()
        self.latest_id = latest_id         # Update latest ID
        self.__writeLatestID()
        News.q_pattern = self.q_pattern    # Set static variable for class News
        if latest_id > self.last_id:       # Sync is needed
            output.debug("News detected. Begin to sync...")
            for id in init_ids:
                new = None
                try:
                    news = News(id)
                except UnicodeDecodeError: # Ignore decoding error from source HTML (GB2312)
                    continue
                src = news.getNews()
                #print src
                if isValidNews(src, INVALID_PATTERN):            
                    news = self._filter(news, EXCEPTION_LIST, SUB_FILTER, self.api_url)
                    output.debug(news.getWiki())
                    self.wikinews.append(news)
                    
            while len(self.wikinews) < self.num:   # If number of wiki news is less than num
                n_id = ustb.getNextID()            # Get next news until sufficient
                news = News(n_id)
                src = news.getNews()
                #print src
                if isValidNews(src, INVALID_PATTERN):            
                    news = self._filter(news, EXCEPTION_LIST, SUB_FILTER, self.api_url)
                    output.debug(news.getWiki())
                    self.wikinews.append(news)
                    
            self.wikinews = sorted(self.wikinews, key=lambda t: t.getDate())
            self.__flag = 1
            #print self.wikinews
            self._dump()   # Call _put to dump news to local
            #return self.wikinews
            return
     
        else:                         # No sync is needed
            output.debug("There is no need to sync: No news detected.")
            self._writeFlag(False)    # Write flag to indicate no need to sync
            return
            
    def _dump(self):
        """
        Dump self.wikinews to local files
        """
        largest_id = self.getLargestID()
        if largest_id > self.last_id:   # If True, put them on MediaWiki site and update flag file with "00\n"
            output.debug("Retrieving valid news to temporary files...")
            try:
                self._writeFlag(True) # # Write flag to indicate the need to sync
            except:
                output.error("Cannot write flag file.")
                sys.exit(1)
                
            self.__appendNews()
            self.__refreshNews()
            
        else:                           # Else, simply update flag file with empty content
            output.debug("No valid news to retrieve...")
            try:
                self._writeFlag(False)  # Write flag to indicate no need to sync
            except:
                output.error("Cannot write flag file.")
                sys.exit(1)
            
    
    def getLargestID(self):
        """
        Return the largest ID from already-fetched self.wikinews list
        """
        s = sorted(self.wikinews, key=lambda t: t.getID(), reverse=True)
        return s[0].getID()
       
    
    def _writeFlag(self, toSync):
        fn_flag = "/flag"
        
        if toSync:
            ff = open(self.dir + fn_flag, "w")
            ff.write("00\n") 
            ff.close()
        else:
            ff = open(self.dir + fn_flag, "w")
            ff.write("") 
            ff.close()
        
    def __appendNews(self):
        """
        Append latest new news to specific page (temaplte)
        """
        fn_add = "/news_append.txt"   # Filename for to-be-appended (add) news contents
        news_add = []
        for news in self.wikinews:
            if news.getID() > self.last_id:
                news_add.append(news)
        
        _news_add = [ wiki.getWiki(True) for wiki in news_add ] 
        __news_add = "\n\n".join(_news_add)                     # Join referenced news contents with double-newline
        
        output.debug("Writing output file: %s" % fn_add[1:])
        
        try:
            fa = open(self.dir + fn_add, "w")
            fa.write(encode(__news_add))
            fa.close()
            
        except Exception, e:
            output.error("Cannot write to file %s" % fn_add[1:])
            print e
            sys.exit(1)
            
    def __refreshNews(self):
        """
        Refresh news in Current Events page (template)
        """
        fn_ref   = "/news_ref.txt"      # Filename for referenced news contents
        fn_unref = "/news_unref.txt"    # Filename for unreferenced news contents
             
        ref = [ wiki.getWiki(True) for wiki in self.wikinews ]
        unref = [ wiki.getWiki(False) for wiki in self.wikinews ]
        news_ref = "\n\n".join(ref)
        news_unref = "\n\n".join(unref)
        
        news_ref   = self._pywikiFile(bot_tag=self.bot_tag, page=TEMPLATES['news_ref'], text=news_ref)
        news_unref = self._pywikiFile(bot_tag=self.bot_tag, page=TEMPLATES['news_unref'], text=news_unref)
        
        output.debug("Writing output files: %s and %s" % (fn_ref[1:], fn_unref[1:]))
        
        try:
            ff = open(self.dir + fn_ref, "w")
            ff.write(encode(news_ref))
            ff.close()
        except:
            output.error("Cannot write to file %s" % fn_ref[1:])
            sys.exit(1)
        
        try:    
            fu = open(self.dir + fn_unref, "w")
            fu.write(encode(news_unref))
            fu.close()
        except:
            output.error("Cannot write to file %s" % fn_unref[1:])
            sys.exit(1)
        
    def _pywikiFile(self, bot_tag, page, text):
        """
        Make contents into Pywikipedia-readable uploadable text file by adding tags
        
        @param text: original wiki text
        @param bot_tag: bot tag as HTML comments
        @param page: target page title at MediaWiki site
        """
        
        s = u"AAAA{0}TTTT{1}TTTT\n{2}\nBBBB".format(bot_tag, page, text) # AAAA is start mark, TTTT is title mark and BBBB is end mark
        return s
        
    def _updateNewsID(self):
        """
        Update news.id with the latest ID (largest ID)
        """

    def _filter(self, news, exception, subfilter, api_url):
        """
        Apply semantic parse, sub filter and wiki filter processes
        """
        src = news.getNews()
        cand = semanticParse(src, self.api_url)
        s = subFilter(src, subfilter)
        t = wikiFilter(s, news.getDate(), cand, news.getNews(), news.getURL(), exception)
        news.setWiki(t)
        return news
    
    def __writeLatestID(self):
        """
        Update news.id file
        """
        output.debug("Writing latest ID to news.id...")
        try:
            f = open(self.dir + "/news.id", "w")
            f.write(str(self.latest_id))
            f.close()
            
        except Exception, e:
            output.error("Cannot write news.id.")
            #print e
            sys.exit(1)
            
    def __readLastID(self):
        """Read the news.id in local storage to get the last-synced latest Article ID"""
        try:
            fname = self.dir + "/news.id"
            r = ""
            if os.path.isfile(fname):
                f = open(fname, "r")
                r = f.readline()
                f.close()
            else:
                output.warning("news.id does not exist in the given directory. Creating empty news.id")
                f = open(fname, "w")
                r = f.readline()
                f.close()
                
            r = r.strip()
            if r:
                try:
                    r = int(r)
                    return r
                except ValueError:
                    output.error("The content of news.id is not number")
                    sys.exit(1)
            else:
                return -1  # If content is empty, return -1
                
        except:
            output.error("Error reading or creating news.id")
            sys.exit(1)
            
  
    def __checkDir(self, dir):
        """Check validity of dir"""
        d = os.path.abspath(dir) 
        if os.path.isdir(d):
            return dir
        else:
            output.error("The given directory: %s does not exist." % d)
            sys.exit(1)
            
    def __str__(self):
        if self.__flag < 0:
            return "WikiNews object has just been initialized, URL(s) being: \n" + self.url.__str__()
        else:
            t = [ wiki.getWiki() for wiki in self.wikinews ]
            return "\n".join(t)

if __name__ == '__main__':
    test_url = ["http://news.ustb.edu.cn/html/Article_Class2_1_1.html", "http://news.ustb.edu.cn/html/Article_Class2_1_2.html"]
    #u = URL(test_url)
    #print u
    ustb = USTBNewsURL(url = test_url,
                       pattern = r"Article_Show\.asp\?ArticleID=(\d+)",
                       start_id=31718,
                       )
    ustb.getIDs()
    print ustb.getAllIDs()
    print ustb
    print ustb.getNextID()
    print ustb.getNextID()
    print ustb.getAllIDs()
