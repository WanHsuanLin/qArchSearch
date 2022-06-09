#!/bin/bash
# ./exp_compiler.sh h hh device_set/hh/qcnn/8-4-2_gs_d.json qcnn qcnn/8-4-2.qasm
# ./exp_compiler.sh h grid device_set/hh/qcnn/8-4-2_gs_d.json qcnn qcnn/8-4-2.qasm
# ./exp_compiler.sh h hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 0
# ./exp_compiler.sh h grid device_set/hh/qaoa/8_0_gs_d.json qaoa 8 0
# ./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 0
heuristic=$1
device_set=$2
device_spec=$3
max_memory_usage=0
benchmarks=$4
circuit=$5
size=$5
trial=$6

if [ ! -d "results_diff_compiler/$device_set" ]; then 
    mkdir "results_diff_compiler/$device_set"
fi

if [ ! -d "results_diff_compiler/$device_set" ]; then
    mkdir "results_diff_compiler/$device_set"
fi

if [ ! -d "results_diff_compiler/$device_set/$benchmarks" ]; then
    mkdir "results_diff_compiler/$device_set/$benchmarks"
fi

folderName="results_diff_compiler/$device_set/$benchmarks"

if [ "$heuristic" == "h" ]; then
    if [ "$benchmarks" == "qcnn" ]; then
        python3 -u run_heuristic_compiler.py $device_set $device_spec $benchmarks $folderName --filename $circuit | tee "$folderName/output_h_qcnn.log"
    fi

    if [ "$benchmarks" == "qaoa" ]; then
        python3 -u run_heuristic_compiler.py $device_set $device_spec $benchmarks $folderName --size $size --trial $trial | tee "$folderName/output_h_qaoa.log"
    fi
fi

if [ "$heuristic" == "o" ]; then
    if [ "$benchmarks" == "qcnn" ]; then
        python3 -u run_optimal_compiler.py $device_set $device_spec $benchmarks $folderName --filename $circuit | tee "$folderName/output_o_qcnn.log"
    fi

    if [ "$benchmarks" == "qaoa" ]; then
        python3 -u run_optimal_compiler.py $device_set $device_spec $benchmarks $folderName --size $size --trial $trial | tee "$folderName/output_o_qaoa_${size}_${trial}.log"
    fi
fi

