#!/bin/bash
# ./exp.sh qcnn qcnn/8-4-2.qasm
trap "exit" INT

device_set=$1
benchmarks=$2

if [ "$benchmarks" == "qcnn" ]; then
    circuit=$3
    substring=".qasm"
    mode=$4
fi

if [ "$benchmarks" == "qaoa" ]; then
    size=$3
    trial=$4
    mode=$5
fi

max_memory_usage=0

if [ ! -d "results/$device_set" ]; then 
    mkdir "results/$device_set"
fi

if [ ! -d "results/$device_set/$mode" ]; then
    mkdir "results/$device_set/$mode"
fi

# for circuit in $benchmarks/*; do
# echo $circui

if [ "$benchmarks" == "qcnn" ]; then
    folderName="results/$device_set/$mode/${circuit%"$substring"}"
    if [ ! -d "$folderName"    ]; then 
        mkdir $folderName   
    fi
    python3 -u run_qas.py $device_set $benchmarks $folderName --filename $circuit --memory_max_size $max_memory_usage | tee "$folderName/output.log"
fi

if [ "$benchmarks" == "qaoa" ]; then
    folderName="results/$device_set/$mode/$size_$trial"
    if [ ! -d "$folderName"    ]; then 
        mkdir $folderName   
    fi
    python3 -u run_qas.py $device_set $benchmarks $folderName --size $size --trial $trial --memory_max_size $max_memory_usage | tee "$folderName/output.log"
fi

echo "all done"
