#!/bin/bash
# sync all files (matching against the filtering rule) in the working directory to a remote/local directory
# usage:
# cd work_dir
# ./rsync_this.sh /local/or/remote/path/ 
rsync -avz -e ssh -f"- .*" -f"- rsync_this.sh" -f"+ *" ./ $1
