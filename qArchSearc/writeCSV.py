import argparse
import json
import csv
import pandas as pd
import numpy as np
from util import get_list_of_json_files

def create_list_from_json(jsonfile:str):
    with open(jsonfile) as f:
        data = json.load(f)
    data_list = []  # create an empty list

    # append the items to the list in the same order.
    data_list.append(data.get('M'))
    data_list.append(data.get('D'))
    data_list.append(data.get('g1'))
    data_list.append(data.get('g2'))
    data_list.append(data.get('extra_edge_num'))
    data_list.append(data.get('extra_edge'))
    data_list.append(data.get('cost'))
    data_list.append(data.get('fidelity'))
    data_list.append(data.get('cost-scaled fidelity'))
    data_list.append(data.get('crosstalk'))
    data_list.append(data.get('fidelity_ct'))
    data_list.append(data.get('cost-scaled fidelity_ct'))
    
    return data_list

def write_csv():
    list_of_files = get_list_of_json_files(args.folder)
    tmpStr = args.folder.split('/')
    csv_name = '_f.csv'
    for i, s in enumerate(reversed(tmpStr)):
        if i == 0:
            csv_name = s + csv_name
        if i == 1:
            csv_name = s + '/csv/' + csv_name
        else:
            csv_name = s + '/' + csv_name

    with open(csvName, 'w+') as c:
        writer = csv.writer(c)
        writer.writerow(['M', 'D', 'g1', 'g2', 'extra_edge_num', \
        'extra_edge', 'cost', 'fidelity', 'cost-scaled fidelity', 'crosstalk', 'fidelity_ct', 'cost-scaled fidelity_ct']
    c.close()
    for file in list_of_files:
        row = create_list_from_json(file)  # create the row to be added to csv for each file (json-file)
        with open(csvName, 'a') as c:
            writer = csv.writer(c)
            writer.writerow(row)
        c.close()
    df = pd.read_csv(csvName)
    cal_fid_dec(df)
    cal_crosstalk_ratio(df)

    sorted_df = df.sort_values(by=['extra_edge_num'])  
    
    cal_improve_ratio(sorted_df)
    sorted_df = sorted_df.reset_index(drop=True)

    sorted_df.to_csv(csvName, index=False)

def cal_fid_dec(df):
    df['fidelity_dec_ratio'] = (df['fidelity']-df['fidelity_ct'])/df['fidelity']

def cal_crosstalk_ratio(df):
    df['ct_ratio'] = df['crosstalk'] / df['g2']

def cal_improve_ratio(df):
    baseLine = df.iloc[0]['fidelity']
    df['f_improve_r'] = (df['fidelity']-baseLine) / baseLine

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("folder", metavar='folder', type=str,
        help="Result Folder: each benchmark result")
    parser.add_argument("benchmark", metavar='B', type=str,
        help="Benchmark Set: arith or qaoa or QCNN")
    # Read arguments from command line
    args = parser.parse_args()
    write_csv()