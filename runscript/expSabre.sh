#!/bin/bash
# Reference of the bash script: https://unix.stackexchange.com/a/436713
# To run this, use `bash exp.sh` in this directory

# The number of tasks to run at the same time.
N=2

# There are two constraints: how many cores in your CPU and how much memory.
# Use `lscpu` to see how many cores you have; use `free` to check memory usage.
# Usually we leave some room for the hosting system as well.

trap "exit" INT
benchmarks="qcnn_sabre"
substring=".qasm"

# Iterate over some devices. Increasing the upper bound to 255 means all the devices.
if [ ! -d "results_sabre/256/basic/$benchmarks" ]; then 
    cd "results_sabre/256/basic/"
    mkdir $benchmarks
    cd ../../../
fi

if [ ! -d "results_sabre/256/decay/$benchmarks" ]; then 
    cd "results_sabre/256/decay/"
    mkdir $benchmarks
    cd ../../../
fi

if [ ! -d "results_sabre/256/lookahead/$benchmarks" ]; then 
    cd "results_sabre/256/lookahead/"
    mkdir $benchmarks
    cd ../../../
fi

# for circuit in $benchmarks/*; do
for circuit in $benchmarks/*; do
    # echo $circuit
    folderName="results_sabre/256/basic/${circuit%"$substring"}"
    # echo $folderName
    prefifx="results_sabre/256/basic/$benchmarks/"
    # echo $prefifx
    cd $prefifx
    mkdir ${folderName#"$prefifx"}
    cd ../../../../
    for i in {0..255}; do
        # for j in {1..9}; do
            (   
                python3 runSabre.py qcnn $i $folderName --filename $circuit

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


for circuit in $benchmarks/*; do
    # echo $circuit
    folderName="results_sabre/256/lookahead/${circuit%"$substring"}"
    # echo $folderName
    prefifx="results_sabre/256/lookahead/$benchmarks/"
    # echo $prefifx
    cd $prefifx
    mkdir ${folderName#"$prefifx"}
    cd ../../../../
    for i in {0..255}; do
        # for j in {1..9}; do
            (   
                python3 runSabre.py qcnn $i $folderName --filename $circuit --lookahead

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

for circuit in $benchmarks/*; do
    # echo $circuit
    folderName="results_sabre/256/decay/${circuit%"$substring"}"
    # echo $folderName
    prefifx="results_sabre/256/decay/$benchmarks/"
    # echo $prefifx
    cd $prefifx
    mkdir ${folderName#"$prefifx"}
    cd ../../../../
    for i in {0..255}; do
        # for j in {1..9}; do
            (   
                python3 runSabre.py qcnn $i $folderName --filename $circuit --decay

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
