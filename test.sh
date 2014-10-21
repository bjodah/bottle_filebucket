#!/bin/bash
python bottle_filebucket.py &
PID=$!
sleep 3 # give the server a chance to start
mkdir temp/
oricwd=$(pwd)
function finish {
    cd $oricwd
    rm -r temp/
    kill $PID
}
trap finish EXIT
cd temp/
echo A >file1.txt
curl -i -X PUT -F token=BLS4G66XHBGOI -F filename=file2.txt -F filedata=@file1.txt --insecure "https://localhost:8081/upload"
if [[ `cat ../file2.txt` != `cat file1.txt` ]]; then
    echo "Test FAILED!"
    exit 1
fi
echo "Test PASSED!"
