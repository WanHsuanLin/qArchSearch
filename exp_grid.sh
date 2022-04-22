#!/bin/bash
# ./exp.sh qcnn qcnn/8-4-2.qasm
trap "exit" INT

device_set="grid"
mode=1
max_memory_usage=0

if [ ! -d "results/$device_set" ]; then 
    mkdir "results/$device_set"
fi

if [ ! -d "results/$device_set/$mode" ]; then
    mkdir "results/$device_set/$mode"
fi


for benchmarks in qcnn qaoa; do
    if [ ! -d "results/$device_set/$mode/$benchmarks" ]; then
        mkdir "results/$device_set/$mode/$benchmarks"
    fi
    if [ "$benchmarks" == "qcnn" ]; then
        circuit_set="qcnn/8-4-2.qasm qcnn/10-5-3-2.qasm qcnn/12-6-3-2.qasm"
        substring=".qasm"
    fi

    if [ "$benchmarks" == "qaoa" ]; then
        size=$3
        trial=0
    fi

    if [ "$benchmarks" == "qcnn" ]; then
        for circuit in $circuit_set; do
            echo $circuit
            folderName="results/$device_set/$mode/${circuit%"$substring"}"
            if [ ! -d "$folderName"    ]; then 
                mkdir $folderName   
            fi
            python3 -u runArchSearch.py $device_set $benchmarks $folderName --filename $circuit --mode $mode --memory_max_size $max_memory_usage | tee "$folderName/output.log"
        done
    fi

    if [ "$benchmarks" == "qaoa" ]; then
        for trial in 0 1 2 3 4; do
            for size in 8 10 12; do
                folderName="results/$device_set/$mode/qaoa/${size}_${trial}"
                if [ ! -d "$folderName"    ]; then 
                    mkdir $folderName   
                fi
                python3 -u runArchSearch.py $device_set $benchmarks $folderName --size $size --trial $trial --mode $mode --memory_max_size $max_memory_usage | tee "$folderName/output.log"
            done
        done
    fi
done



echo "all done"
