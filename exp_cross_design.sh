#!/bin/bash
#./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 2
#./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 7
#./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 7  
#./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 8
#./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 8
#./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 9
#./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 9  
#./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 10
#./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 10
# ./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 11
# ./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 11
# ./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 12
# ./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 12
# ./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 13
# ./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 13
# ./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 14
# ./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 14
# ./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 15
# ./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 15

for i in 2 5 7 8 10; do
    (   
        ./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 $i
        ./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 $i

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

for i in {13..30}; do
    (   
        ./exp_compiler.sh o hh device_set/hh/qaoa/8_0_gs_d.json qaoa 8 $i
        ./exp_compiler.sh o grid device_set/grid/qaoa/8_0_gs_d.json qaoa 8 $i

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

    