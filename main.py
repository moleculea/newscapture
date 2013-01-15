# -*- coding: utf-8  -*-
import news
from conf import *
def main():
    dir       = FILE_DIR
    url       = INDEX_URL
    num       = NEWS_NUM
    pattern   = ID_PATTERN
    q_pattern = Q_PATTERN
    api_url   = API_URL
    
    # Creating Wikinews object and invoke start()
    wiki = news.WikiNews(dir, url, num, pattern, q_pattern, api_url)
    wiki.start()

if __name__ == '__main__':
    main()