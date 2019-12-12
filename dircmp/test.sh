#!/bin/bash
echo "Running tests"

echo "python dircmp.py tests/default/src tests/default/dst"
echo "python dircmp.py tests/default/src tests/default/dst" > test-log.txt
python dircmp.py tests/default/src tests/default/dst >> test-log.txt
echo "python dircmp.py -a tests/default/src tests/default/dst"
echo "python dircmp.py -a tests/default/src tests/default/dst" >> test-log.txt
python dircmp.py -a tests/default/src tests/default/dst >> test-log.txt
echo "python dircmp.py -r tests/default/src tests/default/dst"
echo "python dircmp.py -r tests/default/src tests/default/dst" >> test-log.txt
python dircmp.py -r tests/default/src tests/default/dst >> test-log.txt
echo "python dircmp.py -a -r tests/default/src tests/default/dst"
echo "python dircmp.py -a -r tests/default/src tests/default/dst" >> test-log.txt
python dircmp.py -a -r tests/default/src tests/default/dst >> test-log.txt

echo "python dircmp.py tests/hidden/src tests/hidden/dst"
echo "python dircmp.py tests/hidden/src tests/hidden/dst" >> test-log.txt
python dircmp.py tests/hidden/src tests/hidden/dst >> test-log.txt
echo "python dircmp.py -a tests/hidden/src tests/hidden/dst"
echo "python dircmp.py -a tests/hidden/src tests/hidden/dst" >> test-log.txt
python dircmp.py -a tests/hidden/src tests/hidden/dst >> test-log.txt
echo "python dircmp.py -r tests/hidden/src tests/hidden/dst"
echo "python dircmp.py -r tests/hidden/src tests/hidden/dst" >> test-log.txt
python dircmp.py -r tests/hidden/src tests/hidden/dst >> test-log.txt
echo "python dircmp.py -a -r tests/hidden/src tests/hidden/dst"
echo "python dircmp.py -a -r tests/hidden/src tests/hidden/dst" >> test-log.txt
python dircmp.py -a -r tests/hidden/src tests/hidden/dst >> test-log.txt

echo "python dircmp.py tests/tree/src tests/tree/dst"
echo "python dircmp.py tests/tree/src tests/tree/dst" >> test-log.txt
python dircmp.py tests/tree/src tests/tree/dst >> test-log.txt
echo "python dircmp.py -a tests/tree/src tests/tree/dst"
echo "python dircmp.py -a tests/tree/src tests/tree/dst" >> test-log.txt
python dircmp.py -a tests/tree/src tests/tree/dst >> test-log.txt
echo "python dircmp.py -r tests/tree/src tests/tree/dst"
echo "python dircmp.py -r tests/tree/src tests/tree/dst" >> test-log.txt
python dircmp.py -r tests/tree/src tests/tree/dst >> test-log.txt
echo "python dircmp.py -a -r tests/tree/src tests/tree/dst"
echo "python dircmp.py -a -r tests/tree/src tests/tree/dst" >> test-log.txt
python dircmp.py -a -r tests/tree/src tests/tree/dst >> test-log.txt

echo "Inspect test-log.txt as compared with master-test-log.txt,"
echo "    ignore timings and timestamps"
echo "Automated comparisons, may be coming soon :)"
