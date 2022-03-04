#!/bin/bash

for j in {0..10}; do
    echo "n=2, size=4, trial=$j"
    python3 olsqDumpConstraint.py 2 "olsqScability/fix_depth" --size 4 --bound_depth 21 --trial $j --numSwap -1
done

python3 olsqDumpConstraint.py 3 "olsqScability/fix_depth" --size 4 --bound_depth 21 --trial 0 --numSwap -1
python3 olsqDumpConstraint.py 3 "olsqScability/fix_depth" --size 6 --bound_depth 21 --trial 0 --numSwap -1

for j in {0..8}; do
    python3 olsqDumpConstraint.py 3 "olsqScability/fix_depth" --size 8 --bound_depth 21 --trial $j --numSwap -1
done

python3 olsqDumpConstraint.py 4 "olsqScability/fix_depth" --size 4 --bound_depth 21 --trial 0 --numSwap -1
python3 olsqDumpConstraint.py 4 "olsqScability/fix_depth" --size 6 --bound_depth 21 --trial 0 --numSwap -1
python3 olsqDumpConstraint.py 4 "olsqScability/fix_depth" --size 8 --bound_depth 21 --trial 0 --numSwap -1
python3 olsqDumpConstraint.py 4 "olsqScability/fix_depth" --size 10 --bound_depth 21 --trial 0 --numSwap -1
python3 olsqDumpConstraint.py 4 "olsqScability/fix_depth" --size 12 --bound_depth 21 --trial 0 --numSwap -1
python3 olsqDumpConstraint.py 4 "olsqScability/fix_depth" --size 14 --bound_depth 21 --trial 0 --numSwap -1

for j in {0..4}; do
    python3 olsqDumpConstraint.py 4 "olsqScability/fix_depth" --size 16 --bound_depth 21 --trial $j --numSwap -1
done

for i in 4 6 8 10 12 14 16 18 20 22 24; do
    for j in {5..9}; do
        python3 olsqDumpConstraint.py $j "olsqScability/fix_depth" --size $i --bound_depth 21 --trial 0 --numSwap -1
    done
done
