#!/bin/bash
# Reference of the bash script: https://unix.stackexchange.com/a/436713
# To run this, use `bash exp.sh` in this directory

# The number of tasks to run at the same time.
N=2

# There are two constraints: how many cores in your CPU and how much memory.
# Use `lscpu` to see how many cores you have; use `free` to check memory usage.
# Usually we leave some room for the hosting system as well.

trap "exit" INT
benchmarks="qcnn_tket"
substring=".qasm"

for i in {0..255}; do
    (   
        python3 runtket.py qcnn $i results_tket/256/default/qcnn/8 --filename qcnn_tket/8.qasm 

        echo "started task $i.."
        sleep $(( (RANDOM % 3) + 1))
    ) &

    # allow to execute up to $N jobs in parallel
    if [[ $(jobs -r -p | wc -l) -ge $N ]]; then
        # now there are $N jobs already running, so wait here for any job
        # to be finished so there is a place to start next one.
        wait -n
    fi
done
# no more jobs to be started but wait for pending jobs
# (all need to be finished)
wait

echo "all done"
