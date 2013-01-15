# -*- coding: utf-8  -*-
import unittest
import newsprocess
import datetime
import news
import pdb
    
class TestParseURL(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    def Sem(self):
        source = u"北京科技大学"
        api_url = "http://wiki.ibeike.com/api.php" 
        print newsprocess.semanticParse(source, api_url)
        
    def testDate(self): 
        d = datetime.date(2013, 1, 8)
        print newsprocess._wikiDate("Foo", d)
        
    def WikiNews(self):
        dir = "/Users/shichao/Documents/test/"
        url = [
               "http://news.ustb.edu.cn/html/Article_Class2_1_1.html", 
               "http://news.ustb.edu.cn/html/Article_Class2_1_2.html"
               ]
        num = 4
        pattern = r"Article_Show\.asp\?ArticleID=(\d+)"
        q_pattern = "http://news.ustb.edu.cn/html/article/Article_show%s.html"
        api_url = "http://wiki.ibeike.com/api.php" 
        #pdb.set_trace()
        wiki = news.WikiNews(dir, url, num, pattern, q_pattern, api_url)
        print wiki
        wiki.start()
        #wiki.put()
        #print wiki
        
if __name__ == '__main__':
    unittest.main()
