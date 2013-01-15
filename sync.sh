#!/bin/bash
script_folder=/home/anshichao/newscapture/
file_folder=${script_folder}local/
py_path=/usr/bin/python
pywikipedia=/root/pywikipedia/
news_ref=news_ref.txt
news_unref=news_unref.txt
news_add=news_append.txt
flag=flag
wiki_site=wiki.ibeike.com

# Execute Python scripts to dump temp files
$py_path ${script_folder}main.py

if [ "$?" -ne 0 ]
then 
	exit 1
else

	
	# Check the size of flag file
	fsize=$(cat $file_foler$flag | wc -c)
	if [ "$fsize" -gt 2 ]
	then
		echo "Syncing $news_ref and $news_unref to $wiki_site..."
		
		# Import referenced news to Template:NewsAuto
		$py_path ${pywikipedia}pagefromfile.py -start:AAAA -end:BBBB -titlestart:TTTT -titleend:TTTT -file:$file_folder$news_ref -force -notitle	
		# Import referenced news to Template:NewsAutoUntagged
		$py_path ${pywikipedia}pagefromfile.py -start:AAAA -end:BBBB -titlestart:TTTT -titleend:TTTT -file:$file_folder$news_unref -force -notitle
		
		echo "Syncing $news_add to $wiki_site..."
		
		# Add referenced appended news to Template:NewsUpdate
		$py_path ${pywikipedia}add_text.py -textfile:$file_folder$news_add -page:Template:NewsUpdate -bottom -always

		echo "Sync accomplished."
		
	else
		echo "No newly dumped files detected. Sync terminated."
	fi

	echo
fi
exit 0

