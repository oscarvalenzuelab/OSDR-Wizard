#!/bin/bash
URL="https://raw.githubusercontent.com/spdx/license-list-data/master/licenses.md"
curl -v --silent $URL 2>&1 | grep '\]\[\]' | awk -F'[][]' '{print $1 $2}' | sed 's/  */ /g'>licenses.temp
ID=1
echo '' > spdx.sql
while IFS= read -r line
do
  NAME=$(echo $line | cut -d '|' -f2 |tr -d '"'| sed -n '1h;1!H;${;g;s/^[ \t]*//g;s/[ \t]*$//g;p;}')
  SPDX=$(echo $line | cut -d '|' -f3 | sed -n '1h;1!H;${;g;s/^[ \t]*//g;s/[ \t]*$//g;p;}')
  echo 'INSERT INTO licenses VALUES ('$ID',"'$NAME' ['$SPDX'])","'$SPDX'");' >> spdx.sql
  let ID=ID+1
done < "licenses.temp"
rm -rf "licenses.temp"
