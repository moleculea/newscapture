# -*- coding: utf-8  -*-

"""
Main configuration
"""

"""
    * FILE_DIR        : location for input and output files (ended with slash /)
    * INDEX_URL       : list of URLs for source index pages of news
    * NEWS_NUM        : number of news to capture at one time
    * ID_PATTERN      : pattern for matching news ID
    * Q_PATTERN       : quasi-pattern URL string for substituting news ID
    * API_URL         : URL of MediaWiki API (URI of path to api.php)
    * INVALID_PATTERN : nullify news that match any patterns listed
    * SUB_FILTER      : replacement patterns
    * EXCEPTION_LIST  : exceptions for semantic parse matching which generates wiki links
    * TEMPLATES       : dictionary mapping target template page at MediaWiki sites

"""
FILE_DIR     = "/home/anshichao/newscapture/local/"
INDEX_URL    = [
                "http://news.ustb.edu.cn/html/Article_Class2_1_1.html", 
                "http://news.ustb.edu.cn/html/Article_Class2_1_2.html",
               ]

NEWS_NUM    = 4
ID_PATTERN  = r"Article_Show\.asp\?ArticleID=(\d+)"
Q_PATTERN   = "http://news.ustb.edu.cn/html/article/Article_show%s.html"
API_URL     = "http://wiki.ibeike.com/api.php" 
INVALID_PATTERN = [
                   u"^.+：",        # Derivative news prefix (e.g. 光明日报：)
                   u"【视频】",      # Those with [Video] tags
                   r"\S+\s+\S+",    # Those with whitespace(s) in the middle
                   r"\S+&nbsp;\S+", # Those with HTML whitespace in the middle
                   ] 

SUB_FILTER = {
              u".+——(.+)" : r"\1",   # Preserve text after "--"
              u"我校"       : u"北京科技大学",
              u"我国"       : u"中国",
              }

EXCEPTION_LIST = [
                  u"北京科技大学", 
                  u"北京科技大"
                  ]

TEMPLATES = {
                 'news_ref'  :  u"Template:NewsAuto",
                 'news_unref':  u"Template:NewsAutoUntagged",
                 }
