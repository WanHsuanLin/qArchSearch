#!/bin/bash
# ./exp.sh qcnn qcnn/8-4-2.qasm
trap "exit" INT

benchmarks=$1

if [ "$benchmarks" == "qcnn" ]; then
    circuit=$2
    substring=".qasm"
    mode=$3
    max_memory_usage=$4

if [ "$benchmarks" == "qaoa" ]; then
    size=$2
    trial=$3
    mode=$4
    max_memory_usage=$5

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
    python3 -u runArchSearch.py $benchmarks $folderName --filename $circuit --mode $mode --memory_max_size $max_memory_usage | tee "$folderName/output.log"

if [ "$benchmarks" == "qaoa" ]; then
    folderName="results/$mode/$size_$trial"
    if [ ! -d "$folderName"    ]; then 
        mkdir $folderName   
    fi
    python3 -u runArchSearch.py $benchmarks $folderName --size $size --trial $trial --mode $mode --memory_max_size $max_memory_usage | tee "$folderName/output.log"

echo "all done"