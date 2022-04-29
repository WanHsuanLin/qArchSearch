#!/bin/bash

device_set=$1
mode=1
max_memory_usage=0
benchmarks=$2
circuit=$3
size=$3
trial=$4

if [ ! -d "results_diff_compiler/$device_set" ]; then 
    mkdir "results_diff_compiler/$device_set"
fi

if [ ! -d "results_diff_compiler/$device_set/$mode" ]; then
    mkdir "results_diff_compiler/$device_set/$mode"
fi

if [ ! -d "results_diff_compiler/$device_set/$mode/$benchmarks" ]; then
    mkdir "results_diff_compiler/$device_set/$mode/$benchmarks"
fi

folderName="results_diff_compiler/$device_set/$mode/$benchmarks"
if [ "$benchmarks" == "qcnn" ]; then
    python3 -u run_heuristic_compiler.py $device_set $benchmarks $folderName --filename $circuit | tee "$folderName/output.log"
fi

if [ "$benchmarks" == "qaoa" ]; then
    python3 -u run_heuristic_compiler.py $device_set $benchmarks $folderName --size $size --trial $trial | tee "$folderName/output.log"
fi


