#!/bin/bash

# ./analysis.sh qcnn oneEdge/qcnn_circuits --device
# ./analysis.sh qcnn twoEdge/qcnn_circuits --device
# ./analysis.sh arith oneEdge/arith --device
# ./analysis.sh qaoa oneEdge/qaoa --device
# ./analysis.sh qaoa twoEdge/qaoa --device
# ./analysis.sh arith 256/results_ac 
# ≈
# ./analysis.sh qcnn 256/results_qaoa_swap

# ./analysis.sh qcnn oneEdge/qcnn_circuits --device
# ./analysis.sh qcnn oneEdge_olsq/fidelity2/qcnn --device
# ./analysis.sh qcnn sabre/basic/qcnn_sabre --device
# ./analysis.sh qcnn oneEdge/swap/qcnn --device
# ./analysis.sh qcnn results_ibm/qcnn_circuits
# ./analysis.sh qcnn results/results_256/swap/results_QCNN_gsg1 --crosstalk
# for dir in */; do
#     echo "$dir"
# done

# if [ ! -d "$2/csv" ]; then 
#     cd "$2"
#     mkdir "csv"
#     cd ..
# fi

# python3 run/scheduler.py results/results_256/swap/results_QCNN_gsg1ct
# ./analysis.sh qcnn results/results_256/swap/results_QCNN_gsg1ct

python3 run/scheduler.py results/results_256/swap/results_QCNN_gsg1/results_8 results/results_256/swap/results_QCNN_gsg1ct/results_8 --c 1

# for i in $2/* ; do
#   if [ -d "$i" ]; then
#     if [ "$i" != "$2/csv" ] | [ "$i" != "$2/csvgs" ] | [ "$i" != "$2/csvct" ] ; then
#         echo "$i"
#         # python3 analysis_results/calDepth.py $i
#         # python3 gate_absorption.py $i $1
#         python3 run/scheduler.py $2 
#     fi
#   fi
# done

# python3 drawChart.py "results_$2/csv" $1 $3 

# # wrtieCSV : generate csv file for all json files in the given folder and calculate fidelity
# python3 writeCSV.py "results_$1"
# # drawChart : generate figuere to show the cost and the fidelity
# python3 drawChart.py "results_$1_f.csv"
# python3 drawChart.py results_oneEdge/qcnn_circuits/csv oneEdge_qcnn --device
# ython3 drawChart.py "eComparison/qaoa/csv" qaoa comparison_qaoa --comp
# python3 drawChart.py eComparison/olsqTb/csv qcnn --comp
# python3 drawChart.py compilerComparison/qcnn/10 qcnn --device
# python3 drawChart.py results_oneEdge/swap/qcnn/csv qcnn avg_qcnn --avg
# python3 drawChart.py compilerComparison/256/qcnn/8 qcnn compilerComparison/256/qcnn_8
# python3 drawChart.py results_256/swap/results_qaoa_gs/csv qaoa 256/qaoa_gs/qaoa

# ! remember to recalculate the depth of qcnn circuits
# ! remember to recalculate g1 for arithmetic circuits
# for i in results_256/results_ac/* ; do
#   if [ -d "$i" ]; then
#     if [ "$i" != "results_256/results_ac/csv" ]; then
#         echo "$i"
#         python3 calDepth.py results_256/swap/results_qaoa_swap/results_8/
#     fi
#   fi
# done

# To run qv128
# python3 drawChart.py results_256/swap/qv/csvgs qv 256/qv/qvgs
# Best device cost: 61, Best device: 66
# To run QCNN
# python3 analysis_results/drawChart.py results/results_256/swap/results_QCNN_gs/csv qcnn 256/QCNN_gs_ct/qcnn --crosstalk
# 8- Best device cost: 64, Best device: no3
# 10- Best device cost: 64, Best device: 25,37,38,197,202
# 12- Best device cost: 64, Best device: 66,198
# To run QAOA with Itr 
# python3 drawChart.py results_256/swap/qaoaItrCsv qaoa 256/qaoaItr/qaoa      
# To run QAOA
# python3 drawChart.py results_256/swap/results_qaoa_gs/csv qaoa 256/qaoa_gs/qaoa 
