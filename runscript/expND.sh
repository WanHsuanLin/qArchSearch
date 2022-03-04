#!/bin/bash
# Reference of the bash script: https://unix.stackexchange.com/a/436713
# To run this, use `bash exp.sh` in this directory

# The number of tasks to run at the same time.
N=3

# There are two constraints: how many cores in your CPU and how much memory.
# Use `lscpu` to see how many cores you have; use `free` to check memory usage.
# Usually we leave some room for the hosting system as well.

trap "exit" INT
benchmarks="tmp"
substring=".qasm"

# Iterate over some devices. Increasing the upper bound to 255 means all the devices.

if [ ! -d "results_oneEdge/$benchmarks" ]; then 
    cd "results_oneEdge"
    mkdir $benchmarks
    cd ..
fi

for circuit in $benchmarks/*; do
    # echo $circuit
    folderName="results_oneEdge/${circuit%"$substring"}"
    # echo $folderName
    prefifx="results_oneEdge/$benchmarks/"
    # echo $prefifx
    cd $prefifx
    mkdir ${folderName#"$prefifx"}
    cd ../../
    for i in {0..5}; do
        # for j in {1..9}; do
            (   
                # Example of running arithmetic benchmarks. See `python3 runolsq.py --help`.
                # You can try iterate over files by `for circuit in arith_circuits ...`
                
                # python3 runolsqND.py arith $i --filename arith_circuits/rc_adder_6.qasm --comment try_bash_parallel 
                # python3 runolsqND.py arith $i --filename arith_circuits/mod5_4.qasm
                
                # Example of running QAOA benchmarks
                # python3 runolsqND.py qaoa $i folderName --size 12 --trial 0

                # Example of running QCNN benchmarks
                python3 runolsqND.py qcnn $i $folderName --filename $circuit
                # python3 runolsqND.py qcnn $i folderName --filename qcnn_circuits/16-8-4-2.qasm

                echo "started task $i.."
                sleep $(( (RANDOM % 3) + 1))
            ) &

            # allow to execute up to $N jobs in parallel
            if [[ $(jobs -r -p | wc -l) -ge $N ]]; then
                # now there are $N jobs already running, so wait here for any job
                # to be finished so there is a place to start next one.
                wait -n
            fi
        # done

    done
done
# no more jobs to be started but wait for pending jobs
# (all need to be finished)
wait

echo "all done"
