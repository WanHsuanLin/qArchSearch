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
    data_list.append(data.get('device'))
    data_list.append(data.get('M'))
    data_list.append(data.get('D'))
    data_list.append(data.get('g1'))
    data_list.append(data.get('g2'))
    if args.benchmark == "qaoa":
        data_list.append(data.get('trial'))
    if args.ifcrosstalk:
        data_list.append(data.get('crosstalk'))
    return data_list

def write_csv():
    list_of_files = get_list_of_json_files(args.folder)
    # if len(list_of_files) < 100:
    #     return
    tmpStr = args.folder.split('/')
    # csvName = tmpStr[-3] + '/' + tmpStr[-2] + '/csv/' + tmpStr[-1] + '_f.csv'
    # csvName = tmpStr[-4] + '/' + tmpStr[-3] + '/' + tmpStr[-2] + '/csv/' + tmpStr[-1] + '_f.csv'
    csvName = tmpStr[-5] + '/' + tmpStr[-4] + '/' + tmpStr[-3] + '/' + tmpStr[-2] + '/csv/' + tmpStr[-1] + '_f.csv'
    # csvName = tmpStr[0] + '/csv/' + tmpStr[1] + '_f.csv'
    with open(csvName, 'w+') as c:
        writer = csv.writer(c)
        if args.benchmark == "qaoa":
            if args.ifcrosstalk:
                writer.writerow(["device", "M", "D", "g1", "g2", "trial", "crosstalk"])
            else:
                writer.writerow(["device", "M", "D", "g1", "g2", "trial"])
        else:
            if args.ifcrosstalk:
                writer.writerow(["device", "M", "D", "g1", "g2", "crosstalk"])
            else:
                writer.writerow(["device", "M", "D", "g1", "g2"])
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

    sorted_df = df.sort_values(by=['device'])  

    if args.benchmark == "qaoa":
        sorted_df = sorted_df.groupby('device').agg([np.mean])
        sorted_df = sorted_df.rename_axis('device').reset_index()
        sorted_df = sorted_df.columns.to_frame().T.append(sorted_df, ignore_index=True)
        sorted_df.columns = range(len(sorted_df.columns))
        sorted_df = sorted_df.drop(1)
        sorted_df.columns = sorted_df.iloc[0]
        sorted_df = sorted_df.drop(0)
        sorted_df = sorted_df.drop(columns='trial')
    
        cal_improve_ratio(sorted_df, tmpStr[-1])
    sorted_df = sorted_df.reset_index(drop=True)

    sorted_df.to_csv(csvName, index=False)

def cal_fid_dec(df):
    df['fidelity_dec_ratio'] = (df['fidelity']-df['fidelity_ct'])/df['fidelity']

def cal_crosstalk_ratio(df):
    df['ct_ratio'] = df['crosstalk'] / df['g2']

def cal_improve_ratio(df, case):
    baseLine = df.iloc[0]['fidelity']
    df['f_improve_r'] = (df['fidelity']-baseLine) / baseLine
    # df['cost-scaled fidelity'] = (100 * df['f_improve_r']) / df['cost']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("folder", metavar='folder', type=str,
        help="Result Folder: each benchmark result")
    parser.add_argument("benchmark", metavar='B', type=str,
        help="Benchmark Set: arith or qaoa or QCNN")
    parser.add_argument("--device", dest="ifdevice", action='store_true',
        help="if you want to draw curve sorted by the index of device")
    parser.add_argument("--crosstalk", dest="ifcrosstalk", action='store_true',
        help="if you want to consider crosstalk effect")
    parser.add_argument("--comment", dest="comment", type=str,
        help="if you want to comment this run in any way")
    # Read arguments from command line
    args = parser.parse_args()
    write_csv()