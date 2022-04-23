import argparse
import json
import csv
import pandas as pd
from qArchSearch.olsq.util import get_list_of_json_files

def create_list_from_json(jsonfile:str):
    with open(jsonfile) as f:
        data = json.load(f)
    data_list = []  # create an empty list

    # append the items to the list in the same order.
    data_list.append(data.get('M'))
    data_list.append(data.get('D'))
    data_list.append(data.get('g1'))
    data_list.append(data.get('g2'))
    data_list.append(data.get('fidelity'))
    data_list.append(data.get('crosstalk'))
    data_list.append(data.get('fidelity_ct'))
    data_list.append(data.get('extra_edge_num'))
    data_list.append(data.get('extra_edge'))
    
    return data_list

def write_csv(csv_name):
    list_of_files = get_list_of_json_files(args.folder)

    with open(csv_name, 'w+') as c:
        writer = csv.writer(c)
        writer.writerow(['M', 'D', 'g1', 'g2', 'f', 'crosstalk', 'f_ct', '#extra_e', 'extra_edge'])
    c.close()
    for file in list_of_files:
        # print(file)
        tmp_str = file.split('/')
        if tmp_str[-1] == 'output.log':
            continue
        # print(file)
        row = create_list_from_json(file)  # create the row to be added to csv for each file (json-file)
        with open(csv_name, 'a') as c:
            writer = csv.writer(c)
            writer.writerow(row)
        c.close()
    df = pd.read_csv(csv_name)
    cal_fid_dec(df)
    cal_crosstalk_ratio(df)

    sorted_df = df.sort_values(by=['#extra_e'])  
    
    cal_improve_ratio(sorted_df)
    sorted_df = sorted_df.reset_index(drop=True)

    sorted_df.to_csv(csv_name, index=False)
    return sorted_df

def cal_fid_dec(df):
    df['f_dec_ratio'] = (df['f']-df['f_ct'])/df['f']

def cal_crosstalk_ratio(df):
    df['ct_ratio'] = df['crosstalk'] / df['g2']

def cal_improve_ratio(df):
    baseLine = df.iloc[0]['f']
    df['f_imp_r'] = (df['f']-baseLine) / baseLine
    baseLine = df.iloc[0]['f_ct']
    df['f_imp_r_ct'] = (df['f_ct']-baseLine) / baseLine

def get_arch_data(df, idx, mode):
    data = []
    data.append(idx)
    list_e = df['extra_edge'].values.tolist()
    list_f = df['f'+mode].values.tolist()
    lsit_f_imp_r = df['f_imp_r'+mode].values.tolist()
    data.append(list_e[idx])
    data.append(list_f[idx])
    data.append(lsit_f_imp_r[idx])
    return data



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("benchmark", metavar='B', type=str,
        help="Benchmark Set: arith or qaoa or QCNN")
    parser.add_argument("folder", metavar='folder', type=str,
        help="Result Folder: each benchmark result")
    # Read arguments from command line
    args = parser.parse_args()
    tmp_str = args.folder.split('/')
    if not tmp_str[-1] == 'csv':
        r_csv_name = '_r.csv'
        for i, s in enumerate(reversed(tmp_str)):
            if i == 0:
                r_csv_name = s + r_csv_name
            elif i == 1:
                r_csv_name = s + '/csv/' + r_csv_name
            else:
                r_csv_name = s + '/' + r_csv_name
        df = write_csv(r_csv_name)