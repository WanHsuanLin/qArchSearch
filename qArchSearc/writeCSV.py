
import argparse
import json
import csv
import pandas as pd
import numpy as np
from util import get_list_of_json_files, calculateCrosstalk

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
        data_list.append(calculateCrosstalk(data,args.benchmark))
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
    calculateFidelity(df)
    calculateCost(df)
    if args.ifcrosstalk:
        calculateFidelityCrosstalk(df)
        calculateCostCrosstalk(df)
        calculateFidelityDicrease(df)
        calculateCrosstalkRatio(df)

    sorted_df = df.sort_values(by=['device'])
    if (args.ifdevice == True):
        if(args.benchmark == "qcnn" or args.benchmark == "QCNN"):
            calculateImproRatio(sorted_df, tmpStr[-1])
        elif args.benchmark == "qaoa":
            calculateImproRatio(sorted_df, tmpStr[-1])        

    # sorted_df = df.sort_values(by=['cost','device'])
    # sorted_df['corss rank'] = np.arange(0, 256, 1)
    if args.benchmark == "qaoa":
        sorted_df = sorted_df.groupby('device').agg([np.mean])
        sorted_df = sorted_df.rename_axis('device').reset_index()
        sorted_df = sorted_df.columns.to_frame().T.append(sorted_df, ignore_index=True)
        sorted_df.columns = range(len(sorted_df.columns))
        sorted_df = sorted_df.drop(1)
        sorted_df.columns = sorted_df.iloc[0]
        sorted_df = sorted_df.drop(0)
        sorted_df = sorted_df.drop(columns='trial')
        # print(sorted_df)
        # print(list(sorted_df.columns.values))
    
        calculateImproRatio(sorted_df, tmpStr[-1])
    sorted_df = sorted_df.reset_index(drop=True)
    groupSameTopoDevice(sorted_df)

    sorted_df.to_csv(csvName, index=False)


def calculateFidelity(df):
    df['fidelity'] = pow(0.999, df['g1']) * pow(args.twoErr, df['g2']) * np.exp(-(df['M'] * df['D'] - 2 * df['g2'] - df['g1'])/args.co_t)
    # df['fidelity'] = pow(args.twoErr, df['g2']) * np.exp(-(df['M'] * df['D'] - 2 * df['g2'] - df['g1'])/args.co_t)
    # df['fidelity'] = pow(df['fidelity'],5)

def calculateFidelityCrosstalk(df):
    df['fidelity_ct'] = pow(0.999, df['g1']) * pow(args.twoErr, (df['g2']-df['crosstalk'])) * pow(args.twoErrCrosstalk, df['crosstalk']) * np.exp(-(df['M'] * df['D'] - 2 * df['g2'] - df['g1'])/args.co_t)
    # df['fidelity_ct'] = pow(args.twoErr, (df['g2']-df['crosstalk'])) * pow(args.twoErrCrosstalk, df['crosstalk']) * np.exp(-(df['M'] * df['D'] - 2 * df['g2'] - df['g1'])/args.co_t)
    # df['fidelity'] = pow(df['fidelity'],5)

def calculateFidelityDicrease(df):
    df['fidelity_dec_ratio'] = (df['fidelity']-df['fidelity_ct'])/df['fidelity']

def calculateCostCrosstalk(df):
    df['cost-scaled fidelity_ct'] = df['fidelity_ct'] / df['cost']

def calculateCost(df):
    cost = [calCost(device) for device in df['device']]
    df['cost'] = cost
    df['cost-scaled fidelity'] = df['fidelity'] / df['cost']

def calculateCrosstalkRatio(df):
    df['ct_ratio'] = df['crosstalk'] / df['g2']

def calCost(device: int):
    cost = 56  # 2×16+24
    if args.ifdevice == True:
        if device <= 5:
            return 57
        else:
            return 58
    tmp = device
    if tmp % 2 == 1:
        cost += 4
    tmp = tmp // 2
    if tmp % 2 == 1:
        cost += 4
    tmp = tmp // 2
    if tmp % 2 == 1:
        cost += 2
    tmp = tmp // 2
    if tmp % 2 == 1:
        cost += 2
    tmp = tmp // 2
    if tmp % 2 == 1:
        cost += 2
    tmp = tmp // 2
    if tmp % 2 == 1:
        cost += 2
    tmp = tmp // 2
    if tmp % 2 == 1:
        cost += 1
    tmp = tmp // 2
    if tmp % 2 == 1:
        cost += 1
    return cost


def calculateImproRatio(df, case):
    baseLine = df.iloc[0]['fidelity']
    df['f_improve_r'] = (df['fidelity']-baseLine) / baseLine
    # df['cost-scaled fidelity'] = (100 * df['f_improve_r']) / df['cost']

def groupSameTopoDevice(df):
    ls_device = [[4,8,16,32], [5,9,17,33], [6,10,18,34], [7,11,19,35], [12,48], [13,49],
                [14,50], [15,51], [20,24,36,40], [21,25,37,41], [22,26,38,42], [23,27,39,43], [28,44,52,56],
                [29,45,53,57], [30,46,54,58], [31,47,55,59], [64,128], [65,129], [66,130],
                [67,131], [68,72,80,96,132,136,144,160], [69,73,81,97], [70,74,82,98], [71,75,83,99,163],
                [76,112,140,176], [77,113,141,177], [78,114,142,178], [84,104,152,164], [88,100,148,168],
                [196,200,208,224]]
    for s_device in ls_device:
        # print(s_device)
        same_group_cfidelity = np.array([])
        for device in s_device:
            if args.benchmark == "qaoa":
                if args.ifcrosstalk:
                    same_group_cfidelity = np.append(same_group_cfidelity,df.iloc[device,11])
                else:
                    same_group_cfidelity = np.append(same_group_cfidelity,df.iloc[device,8])
            else:
                if args.ifcrosstalk:
                    # print("df.iloc[device,10]")
                    # print(df.iloc[device,10])
                    same_group_cfidelity = np.append(same_group_cfidelity,df.iloc[device,10])
                else:
                    # print("df.iloc[device,7]")
                    # print(df.iloc[device,7])
                    same_group_cfidelity = np.append(same_group_cfidelity,df.iloc[device,7])
                # print(same_group_cfidelity)
                # input()
        device_order = np.argsort(same_group_cfidelity)
        # print(df)
        for device in s_device:
            df.loc[device] =  df.loc[s_device[device_order[-1]]]
            df.loc[device,['device']] = device
        # print(s_device[1:])
        # input()
    
        # print(df)
        # df = df.drop(s_device[1:])
        # print(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("folder", metavar='folder', type=str,
        help="Result Folder: each benchmark result")
    # parser.add_argument("--fidelity", dest="f", type=int,
    #     help="The index of fidelity function: TODO")
    parser.add_argument("benchmark", metavar='B', type=str,
        help="Benchmark Set: arith or qaoa or QCNN")
    parser.add_argument("--twoErr", dest="twoErr", type=float, default=0.99,
        help="two qubit error rate")
    parser.add_argument("--twoErrCrosstalk", dest="twoErrCrosstalk", type=float, default=0.985,
        help="two qubit error rate with crosstalk")
    parser.add_argument('--coherence_t', type=int, default=1000,
        help="coherence time", dest='co_t')
    parser.add_argument("--device", dest="ifdevice", action='store_true',
        help="if you want to draw curve sorted by the index of device")
    parser.add_argument("--crosstalk", dest="ifcrosstalk", action='store_true',
        help="if you want to consider crosstalk effect")
    parser.add_argument("--comment", dest="comment", type=str,
        help="if you want to comment this run in any way")
    # Read arguments from command line
    args = parser.parse_args()
    write_csv()


# Group of devices
# {0}
# {1}
# {2}
# {3}
# {4,8,16,32}
# {5,9,17,33}
# {6,10,18,34}
# {7,11,19,35}
# {12,48}
# {13,49}
# {14,50}
# {15,51}
# {20,24,36,40}
# {21,25,37,41}
# {22,26,38,42}
# {23,27,39,43}
# {28,44,52,56}
# {29,45,53,57}
# {30,46,54,58}
# {31,47,55,59}
# {39,43}
# {60}
# {61}
# {62}
# {63}
# {64,128}
# {65,129}
# {66,130}
# {67,131}
# {68,72,80,96,132,136,144,160}
# {69,73,81,97}
# {70,74,82,98}
# {71,75,83,99,163}
# {76,112,140,176}
# {77,113,141,177}
# {78,114,142,178}
# {84,104,152,164}
# {88,100,148,168}
# {192}
# {196,200,208,224}



