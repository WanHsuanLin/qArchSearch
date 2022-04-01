import argparse
import json
import csv
import pandas as pd
import numpy as np
from qArchSearch.util import get_list_of_json_files

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

def write_csv(csv_name):
    list_of_files = get_list_of_json_files(args.folder)

    with open(csv_name, 'w+') as c:
        writer = csv.writer(c)
        writer.writerow(['M', 'D', 'g1', 'g2', '#extra_e', \
        'extra_edge', 'cost', 'f', 'csf', 'crosstalk', 'f_ct', 'csf_ct'])
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
    baseLine = df.iloc[0]['csf']
    df['csf_imp_r'] = df['csf'] / baseLine
    baseLine = df.iloc[0]['csf_ct']
    df['csf_imp_r_ct'] = df['csf_ct'] / baseLine

def get_arch_data(df, idx, mode):
    data = []
    data.append(idx)
    # print("hahaha")
    # print(idx)
    # print(df['extra_edge' + mode])
    # print(df.iloc[[idx], df.columns.get_loc('extra_edge')])
    list_e = df['extra_edge'].values.tolist()
    list_f = df['f'+mode].values.tolist()
    lsit_f_imp_r = df['f_imp_r'+mode].values.tolist()
    lsit_csf_imp_r = df['csf_imp_r'+mode].values.tolist()
    # df.loc[df.index[[idx]], 'extra_edge']
    # df.iloc[[0, 2], df.columns.get_loc('extra_edge')]
    # best_csf.append(df.iloc[[0, 2], df.columns.get_loc('extra_edge')])
    # best_csf.append(df['f' + mode].iloc(idx))
    # best_csf.append(df['f_imp_r' + mode].iloc(idx))
    # best_csf.append(df['csf_imp_r' + mode].iloc(idx))
    data.append(list_e[idx])
    data.append(list_f[idx])
    data.append(lsit_f_imp_r[idx])
    data.append(lsit_csf_imp_r[idx])
    return data

def find_best_architecture(df, csv_name):
    # csf
    np_csf_imp_r = np.array(df['csf_imp_r'])
    max_csf_idx = np.argmax(np_csf_imp_r)
    best_csf = get_arch_data(df, max_csf_idx, '')
    
    # csf_ct
    np_csf_imp_r_ct = np.array(df['csf_imp_r_ct'])
    max_csf_ct_idx = np.argmax(np_csf_imp_r_ct)
    best_csf_ct = get_arch_data(df, max_csf_ct_idx, '_ct')

    # f_imp
    np_f_imp_r = np.array(df['f_imp_r'])
    max_f_imp_r_idx = 0
    best_f_imp = 0
    for i, (f_imp, csf_imp_r) in enumerate(zip(np_f_imp_r, np_csf_imp_r)):
        if best_f_imp < f_imp and csf_imp_r > 1.0:
            max_f_imp_r_idx = i
            best_f_imp = f_imp
    best_f_imp_r = get_arch_data(df, max_f_imp_r_idx, '')
    
    
    # f_ct_imp
    np_f_imp_r_ct = np.array(df['f_imp_r_ct'])
    max_f_imp_r_ct_idx = 0
    best_f_imp_ct = 0
    for i, (f_imp_ct, csf_imp_r_ct) in enumerate(zip(np_f_imp_r_ct, np_csf_imp_r_ct)):
        if best_f_imp_ct < f_imp_ct and csf_imp_r_ct > 1.0:
            max_f_imp_r_ct_idx = i
            best_f_imp_ct = f_imp_ct
    best_f_imp_r_ct = get_arch_data(df, max_f_imp_r_ct_idx, '_ct')


    with open(csv_name, 'w+') as c:
        writer = csv.writer(c)
        writer.writerow(['choose by best csf'])
        writer.writerow(['#e', "edge list", 'f', 'f_imp_r', 'csf_imp_r'])
        writer.writerow(best_csf)

        writer.writerow(['choose by best csf_ct'])
        writer.writerow(['#e', "edge list", 'f_ct', 'f_imp_r_ct', 'csf_imp_r_ct'])
        writer.writerow(best_csf_ct)

        writer.writerow(['choose by largest f_imp with csf > 1'])
        writer.writerow(['#e', "edge list", 'f', 'f_imp_r', 'csf_imp_r'])
        writer.writerow(best_f_imp_r)

        writer.writerow(['choose by largest f_ct_imp with csf_ct > 1'])
        writer.writerow(['#e', "edge list", 'f_ct', 'f_imp_r_ct', 'csf_imp_r_ct'])
        writer.writerow(best_f_imp_r_ct)
    c.close()



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
        c_csv_name = '_choice.csv'
        for i, s in enumerate(reversed(tmp_str)):
            if i == 0:
                r_csv_name = s + r_csv_name
                c_csv_name = s + c_csv_name
            elif i == 1:
                r_csv_name = s + '/csv/' + r_csv_name
                c_csv_name = s + '/csv/' + c_csv_name
            else:
                r_csv_name = s + '/' + r_csv_name
                c_csv_name = s + '/' + c_csv_name
        df = write_csv(r_csv_name)
        find_best_architecture(df, c_csv_name)