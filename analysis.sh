#!/bin/bash

benchmarks=$1
folder=$2

for i in $folder/* ; do
  if [ -d "$i" ]; then
    if [ "$i" != "$folder/csv" ] | [ "$i" != "$folder/csvgs" ] | [ "$i" != "$folder/csvct" ] ; then
        echo "$i"
        python3 analysis.py $1 $i
    fi
  fi
done
