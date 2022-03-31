#!/bin/bash
# ./exp.sh qcnn qcnn/8-4-2.qasm
trap "exit" INT

benchmarks=$1
circuit=$2
substring=".qasm"
max_memory_usage=$3
mode="olsq"

if [ $4 ]; then
    mode="tran"
fi

# Iterate over some devices. Increasing the upper bound to 255 means all the devices.
if [ ! -d "results/$mode/$benchmarks" ]; then 
    mkdir "results/$mode/$benchmarks"
fi

# for circuit in $benchmarks/*; do
# echo $circuit
folderName="results/$mode/${circuit%"$substring"}"
if [ ! -d $folderName    ]; then 
    mkdir $folderName   
fi

python3 -u runArchSearch.py $benchmarks $folderName --filename $circuit --memory_max_size $max_memory_usage $4| tee "$folderName/output.log"

echo "all done"
