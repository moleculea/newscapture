#!/bin/bash
script_foler=/root/newscapture/
file_folder=/root/newscapture/local/
py_path=/usr/bin/python
pywikipedia_path=/root/pywikipedia/
news_ref=news_ref.txt
news_unref=news_unref.txt
news_add=news_add.txt
flag=flag
wiki_site=wiki.ibeike.com

echo "Syncing $news_ref and $news_unref to $wiki_site..."

# Import referenced news to Template:NewsAuto
$py_path ${pywikipedia}pagefromfile.py -start:AAAA -end:BBBB -titlestart:TTTT -titleend:TTTT -file:$file_folder$news_ref

# Import referenced news to Template:NewsAutoUntagged
$py_path ${pywikipedia}pagefromfile.py -start:AAAA -end:BBBB -titlestart:TTTT -titleend:TTTT -file:$file_folder$news_unref

# Check the size of flag file
fsize=$(cat $file_foler$flag | wc -c)
if [ "$fsize" -gt 2 ]
then
	echo "Syncing $news_add to $wiki_site..."
fi

echo "Sync accomplished."
echo
exit 0

