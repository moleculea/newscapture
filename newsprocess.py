# -*- coding: utf-8  -*-
import re
import sys
import urllib
import urllib2
import datetime
import copy
from xml.dom.minidom import parseString
from threading import Thread
from Queue import Queue
from conf import *

def decode(text, source_code='gb2312'):
    """
    Global decoding (from source encoding to Unicode)
    Applied to read() on file-like object (returned by urlopen)
    """
    return text.decode(source_code)

def encode(text, source_code='utf-8'):
    """
    Global encoding (from Unicode to target encoding)
    Applied to write() on file-like object
    """
    return text.encode(source_code)

class output(object):
    """ANSI console colored output"""
    RED     = 1
    GREEN   = 2
    YELLOW  = 3
    ERROR   = 4
    DEBUG   = 5
    WARNING = 6
    @staticmethod
    def __out(type, msg):
        if type == output.ERROR:
            sys.stderr.write("\x1b[1;%dm [%s] %s\x1b[0m\n" % (30 + output.RED, "Error", msg.encode('utf-8')))
        if type == output.DEBUG:
            sys.stdout.write("\x1b[1;%dm [%s] %s\x1b[0m\n" % (30 + output.GREEN, "Debug", msg.encode('utf-8')))
        if type == output.WARNING:
            sys.stdout.write("\x1b[1;%dm [%s] %s\x1b[0m\n" % (30 + output.YELLOW, "Warning", msg.encode('utf-8')))
    @staticmethod
    def error(msg):
        output.__out(output.ERROR, msg)
    @staticmethod    
    def debug(msg):
        output.__out(output.DEBUG, msg)
    @staticmethod   
    def warning(msg):
        output.__out(output.WARNING, msg)

def _parseDate(source):
    """
    Parse date return raw
    """
    sem_pattern = SEM_DATE_PATTERN         # Semantic date pattern 
    sys_pattern = SYS_DATE_PATTERN         # System date pattern
    
    sem_match = re.search(sem_pattern, source)
    sys_match = re.search(sys_pattern, source)

    if sem_match:  # Semantic match has high precedence
        return sem_match
    else:
        return sys_match

            
def retrieveDate(source):
    """
    Return datetime.date object
    """
    match = _parseDate(source)
    year = match.group(1)
    month = match.group(2)
    day = match.group(3)

    if not year:
        year = datetime.date.today().year
    try:
        return datetime.date(int(year), int(month), int(day))
    except TypeError:
        output.error("Error matching month or day in the news page")


def isValidNews(source, pattern_list):
    """
    Determine (return Boolean) where source text is valid for being wiki news
    
    @param source: Unicode source text for news
    @param pattern_list: list pattern which matches invalid text elements
    """
    if len(source) > 40: # Unicode length (number of zh characters) cannot exceed 40
        print len(source)
        output.warning("Invalid news: " + source)
        return False
    
    for pattern in pattern_list:
        if re.search(pattern, source):
            output.warning("Invalid news: " + source)
            return False
    output.debug("Valid news: " + source)
    return True
    
    
def subFilter(source, dictionary):
    """
    Filter source text by substitute, and return filtered source text
    
    @param source: Unicode source text for news
    @param dictionary: dictionary (with precedence) mapping patterns and substitutes
    """
    r = source
    for d in dictionary.items():
        r = re.sub(d[0], d[1], r)
    return r


def wikiFilter(source, date, candidates, original, url, exceptional):
    """
    Filter source text by adding wiki tags 
    * Add link tags ([[ ]]) to titles in the candidates list
    * Reformat date into wiki text
    * Add other customized wiki tags (e.g. templates)
    
    Return the of a 2-tuple of wikified texts, referenced and unreferenced
    
    @param source: Unicode text (after being filtered by subFilter() ) for news
    @param date: datetime.date format
    @param candidates: list of existent titles
    @param orginal: original (unfiltered) news (for external reference)
    @param url: original url of the news page (for external reference)
    @param exceptional: exceptional key words to be filtered out
    """
    cand = []
    if candidates:
        candidates.sort(key=len, reverse=True) # Reversely sort candidates by string length
        # Keep the longest string and filter out any substring titles 
        # (e.g. keep "United States of America" instead of "United States")      
        
        for e in exceptional:    # Filter out exceptional key words
            if e in candidates:
                candidates.remove(e)
                
        for c in candidates:
            output.debug("Matching API: " + c)
            
        cand = copy.deepcopy(candidates)
        
        for i in range(len(candidates)):
            if i > 0:
                for j in range(i):
                    if candidates[i] in candidates[j]:
                        if candidates[i] in cand:
                            cand.remove(candidates[i])
    
    wiki_text = _wikiLink(source, cand)
    wiki_text = _wikiDate(wiki_text, date)             # Add date 
    wiki_text += u"。 "                                # Add full stop to the end
    wiki_text = "* " + wiki_text
    ref_wiki_text = _wikiRef(wiki_text, original, url) # Add reference tag
    
    return (wiki_text, ref_wiki_text)
    
    
def _wikiLink(source, candidates):
    """Add link tags to titles in the candidates list"""
    for c in candidates:
        s = re.sub( u"(" + c + u")", r"[[\1]]", source)
        source = s
    return source

def _wikiDate(wiki_text, date):
    """Reformat date object into wiki date string"""
    month = date.month
    day = date.day
    year = date.year
    this_year = datetime.date.today().year
    tag = ""
    if year == this_year:
        tag = u"{{{{ShowYear|{0}}}}}{1}月{2}日，".format(year, month, day)
    else:
        tag = u"{0}年{1}月{2}日，".format(year, month, day)
    return tag + wiki_text
    
    
def _wikiRef(wiki_text, original, url):
    """Add reference tags"""
    return wiki_text + "<ref>[" + url.__str__() + " " + original + "]</ref>"

        
def semanticParse(source, api_url):
    """
    Parse the source text quasi-semantically and query MediaWiki API (PHP) 
    to check the existence of a certain article (including redirects)
    
    Use multiple threads to speed up API querying
    
    Return candidate titles which exist on MediaWiki sites
    """
    length = len(source) # Number of characters
    candidates = []      # Candidate titles
    r = []
    q = Queue()          # Queue for multithreading
    
    for i in range(length):     
        start_index = i
        end_index   = length
        t = Thread(target=_wordParse, args=(start_index, end_index, api_url, source, q))
        t.start()
    q.join()
    
    try:
        while True:
            candidates.append(q.get(True,2)) # Get all items in queue with timeout (1 second)
    except:
        pass
    #print candidates
    return candidates
    

def _wordParse(start_index, end_index, api_url, source, queue, format="xml"):
    """
    Parse word (threaded) and generate a list for possible title
    """
    titles = []
    for j in range(start_index, end_index + 1):
        titles.append(source[start_index:j])
    _queryAPI(api_url, titles, queue)
               

def _queryAPI(api_url, titles, queue, format="xml"):
    """
    Query MediaWiki with multiple titles (separated by pipelines)
    Return XML
    """
    title = "|".join(titles)
    title_quote = urllib.quote(title.encode('utf-8'))
    url = api_url + "?action=query&titles=%s&format=%s" % (title_quote, format)
    fp = urllib2.urlopen(url)
    xml = fp.read()
    exTitles = _existTitles(xml)
    if exTitles:     # Put every existent title into queue
        for t in exTitles:
            #print t
            queue.put(t)
    return 

def _existTitles(xml):
    """
    Return existent titles by DOM-checking XML (generated by MediaWiki API query)
    """
    exTitles = []
    x = parseString(xml)
    y = x.getElementsByTagName('page')
    for z in y:
        if z.getAttribute('pageid'):
            exTitles.append(z.getAttribute('title'))
    return exTitles

    