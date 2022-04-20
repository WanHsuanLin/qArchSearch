#!/bin/bash
# ./exp.sh qcnn qcnn/8-4-2.qasm
trap "exit" INT

device_set=$1
benchmarks=$2

if [ "$benchmarks" == "qcnn" ]; then
    circuit=$3
    substring=".qasm"
    mode=$4

if [ "$benchmarks" == "qaoa" ]; then
    size=$3
    trial=$4
    mode=$5

max_memory_usage=0

if [ ! -d "results/$mode" ]; then 
    mkdir "results/$mode"
fi

if [ ! -d "results/$mode/$benchmarks" ]; then 
    mkdir "results/$mode/$benchmarks"
fi

# for circuit in $benchmarks/*; do
# echo $circui

if [ "$benchmarks" == "qcnn" ]; then
    folderName="results/$mode/${circuit%"$substring"}"
    if [ ! -d "$folderName"    ]; then 
        mkdir $folderName   
    fi
    python3 -u runArchSearch.py $device_set $benchmarks $folderName --filename $circuit --mode $mode --memory_max_size $max_memory_usage | tee "$folderName/output.log"
fi

if [ "$benchmarks" == "qaoa" ]; then
    folderName="results/$mode/$size_$trial"
    if [ ! -d "$folderName"    ]; then 
        mkdir $folderName   
    fi
    python3 -u runArchSearch.py $device_set $benchmarks $folderName --size $size --trial $trial --mode $mode --memory_max_size $max_memory_usage | tee "$folderName/output.log"
fi

echo "all done"