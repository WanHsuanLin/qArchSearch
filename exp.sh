#!/bin/bash
# ./exp.sh qcnn qcnn/8-4-2.qasm
trap "exit" INT

benchmarks=$1
circuit=$2
substring=".qasm"

# Iterate over some devices. Increasing the upper bound to 255 means all the devices.
if [ ! -d "results/olsq/$benchmarks" ]; then 
    mkdir "results/olsq/$benchmarks"
fi

# for circuit in $benchmarks/*; do
# echo $circuit
folderName="results/olsq/${circuit%"$substring"}"
if [ ! -d $folderName    ]; then 
    mkdir $folderName   
fi

python3 -u runArchSearch.py $benchmarks $folderName --filename $circuit | tee "$folderName/output.log"

echo "all done"
