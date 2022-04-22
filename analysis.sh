#!/bin/bash

benchmarks=$1
folder=$2

mkdir "$folder/csv"

for i in $folder/* ; do
  if [ -d "$i" ]; then
    if [ "$i" != "$folder/csv" ] | [ "$i" != "$folder/csv/" ] ; then
        echo "$i"
        python3 analysis.py $1 $i
    fi
  fi
done
