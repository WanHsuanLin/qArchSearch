#!/bin/bash

for i in 8 10 12 14 16 18 20 22 24; do
    for j in {0..15}; do
        python3 olsqDumpConstraint.py 7 "olsqScability/swap_7" --size $i --bound_depth 21 --trial 0 --numSwap $j
    done
done
