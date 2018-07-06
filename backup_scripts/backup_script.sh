#!/bin/bash
#export $PATH="/home/ubuntu/bin:/home/ubuntu/.local/bin:/home/ubuntu/miniconda2$
#$PATH="/home/ubuntu/.local/bin/aws"
echo "Backing up server"
mysqldump -u rsnuser -p'6$Shadow21' rsn > $(date +%F).sql
# tar -cv $(date +%a) | gzip  ^   $(date +%a).gz
# which aws  ^   /home/ubuntu/backup/log.txt
#echo $BACKUP
aws s3 cp $(date +%F).sql s3://rsn-live
rm $(date +%F).sql