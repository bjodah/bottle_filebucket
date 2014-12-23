#!/bin/bash
nohup python3 bottle_filebucket.py --generate-cert-if-missing &
PID=$!
sleep 3 # give the server a chance to start
mkdir temp/
oricwd=$(pwd)
function finish {
    cd $oricwd
    rm -r temp/
    rm file2.txt
    rm file2.txt.tail1
    rm nohup.out
    kill $PID
}
trap finish EXIT
cd temp/
echo A >file1.txt
curl -i -X PUT -F token=BLS4G66XHBGOI -F filename=file2.txt -F filedata=@file1.txt --insecure "https://localhost:8081/upload"
if [[ `cat ../file2.txt` != `cat file1.txt` ]]; then
    echo "Test FAILED! (files mismatch)"
    exit 1
fi
if [[ `cat ../file2.txt.tail1` != `tail -n 1 file1.txt` ]]; then
    echo "Test FAILED! (second hook failed)"
    exit 1
fi
green='\033[0;32m'
NC='\033[0m' # No Color
echo -e "\nTest ${green}PASSED!${NC}"
exit 0
