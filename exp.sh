#!/bin/bash
# Reference of the bash script: https://unix.stackexchange.com/a/436713
# To run this, use `bash exp.sh` in this directory

# The number of tasks to run at the same time.
N=4

# There are two constraints: how many cores in your CPU and how much memory.
# Use `lscpu` to see how many cores you have; use `free` to check memory usage.
# Usually we leave some room for the hosting system as well.

trap "exit" INT
benchmarks="qcnn_circuits"
substring=".qasm"

# Iterate over some devices. Increasing the upper bound to 255 means all the devices.
if [ ! -d "results/results_256_olsq/swap/$benchmarks" ]; then 
    cd "results/results_256_olsq/swap"
    mkdir $benchmarks
    cd ../../
fi


# for circuit in $benchmarks/*; do
circuit="qcnn_circuits/16-8-4-2.qasm"
    # echo $circuit
    folderName="results/results_256_olsq/swap/${circuit%"$substring"}"

    mkdir $folderName
    for i in {144..255}; do
        # for j in {1..9}; do
            (   
                # Example of running arithmetic benchmarks. See `python3 runolsq.py --help`.
                # You can try iterate over files by `for circuit in arith_circuits ...`
                
                # python3 runolsqND.py arith $i --filename arith_circuits/rc_adder_6.qasm --comment try_bash_parallel 
                # python3 runolsqND.py arith $i --filename arith_circuits/mod5_4.qasm
                
                # Example of running QAOA benchmarks
                # python3 runolsqND.py qaoa $i folderName --size 12 --trial 0

                # Example of running QCNN benchmarks
                # python3 run/runolsq.py qcnn $i $folderName --filename $circuit
                # python3 runolsqND.py qcnn $i folderName --filename qcnn_circuits/16-8-4-2.qasm

                # Example of running QGAN benchmarks
                python3 runolsq.py qcnn $i $folderName --filename $circuit --normal --solve_opt 3
                

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
python3 runolsq.py qcnn 32 $folderName --filename $circuit --normal
# no more jobs to be started but wait for pending jobs
# (all need to be finished)
wait

echo "all done"
