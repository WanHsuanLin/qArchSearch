import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import argparse
import pandas as pd
import numpy as np
import re
import matplotlib.ticker as mticker

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams.update({'font.size': 56})
gMarks1 = ['o','X','D','s','^','p']
gMarks2 = ['.','*','+','s','2','p','1','d','h']
gColors = ['lightcoral','orange','limegreen','cornflowerblue','gray','peru','teal','darkkhaki','slategray']
width = 37
height = 25
linewidth = 14 #default 1.5
markersize = 40

file_type='.png'

def get_list_of_json_files():
    list_of_files = []
    label = []
    # print(args.csv)
    for root, pathnames, files in os.walk(args.csv):
        # print("root :", root)
        for f in files:
            fullpath = os.path.join(root, f)
            list_of_files.append(fullpath)
            # print("fullpath :", fullpath)
            try:
                label.append(int(re.split('_|/',fullpath)[-2]))
            except ValueError:
                label.append(re.split('_|/',fullpath)[-2])
            # print("label :", label)
            
    # sort
    label, list_of_files = zip(*sorted(zip(label, list_of_files),reverse = True))
    return label, list_of_files

def get_bestCf(x):
    df = x.sort_values(by = 'cost-scaled fidelity',ascending=True)
    return df.iloc[-1,:]

def draw_groupBy(title:str, titleAvg:str, list_of_files, label, group:str, feature:str, sort:str, fileName:str, fileNameAvg:str):
    plt.figure(figsize=(width,height))
    # plt.title(title)
    average = np.zeros(num_device)
    for file, c, m, l in zip(list_of_files, gColors, gMarks1, label):
        df = pd.read_csv(file)
        # df_cf = df.groupby(group).agg([np.mean, np.std])
        df_cf = df.groupby(group).agg([np.max])
        if feature == "f_improve_r":
            df_cf = df_cf["fidelity"]
        elif feature == "fct_improve_r":
            df_cf = df_cf["fidelity_ct"]
        else:
            if feature == 'cost-scaled fidelity':
                df_tmp = df_cf["fidelity"]
            elif feature == "cost-scaled fidelity_ct":
                df_tmp = df_cf["fidelity_ct"]
            df_cf = df_cf[feature]
        sorted_df = df_cf.sort_values(by=[sort])
        sorted_df.fillna(0)
        sorted_df.reset_index(inplace=True)
        data = np.array(sorted_df)
        # plot
        elif feature == 'f_improve_r' or feature == "fct_improve_r":
            data[:,1] = data[:,1]/data[0,1]
        if len(average) != len(data[:,1]):
            average = np.zeros(len(data[:,1]))
        average = np.add(average, data[:,1])
        plt.plot(data[:,0], data[:,1], linestyle='--', marker=m, color=c, label=l,linewidth= linewidth, markersize=markersize)
    
    lgd = plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=len(label)+1)
    plt.grid(axis='y')
    plt.xticks(data[:,0])
    plt.xlabel(sort)
    if (args.benchmark == "qaoa" or args.benchmark == "qv") and feature == "f_improve_r":
        plt.axes().set_ylim([-0.03, 0.3])
    if feature == "f_improve_r" or feature == "cost-scaled fidelity" or feature == "cost-scaled fidelity_ct"  or feature == "fidelity_dec_ratio":
        current_values = plt.gca().get_yticks()
        # using format string '{:.0f}' here but you can choose others
        plt.gca().set_yticklabels(['{:,.1%}'.format(x) for x in current_values])
    plt.savefig(fileName, dpi=300, bbox_extra_artists=(lgd,), bbox_inches='tight')
    # plt.savefig(fileName, dpi=300, bbox_inches='tight')
    # plt.figure(figsize=(width,height))
    # plt.title(titleAvg)
    average = np.true_divide(average, len(list_of_files))
    if feature == 'cost-scaled fidelity' or feature == "cost-scaled fidelity_ct":
        print("max possible cf is ", np.max(average))
    plt.plot(data[:,0], average, linestyle='--', marker='d', color='violet', label='average',linewidth= 1.3*linewidth, markersize=1.3*markersize)
    lgd = plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=len(label)+1)
    
    # lgd = plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=len(label)+1)
    # plt.grid(axis='y')
    # plt.xticks(data[:,0])
    # plt.xlabel(sort)
    # plt.tight_layout()
    if feature == 'f_improve_r':
        print("f_impro_r")
        print(average)
    # if feature == 'cost-scaled fidelity':
    #     print(average)
    plt.savefig(fileNameAvg, dpi=300, bbox_extra_artists=(lgd,), bbox_inches='tight')

def draw_normal(title:str, titleAvg:str, list_of_files, label, feature:int, xlabel:str, fileName:str, fileNameAvg:str, ifRankCost = False):
    plt.figure(figsize=(width,height))
    plt.title(title)
    average = np.zeros(num_device)
    for file, c, m, l in zip(list_of_files, gColors, gMarks2, label):
        df = pd.read_csv(file)
        if ifRankCost:
            sorted_df = df.sort_values(by=['cost','device'])
            data = np.array(sorted_df)
        else:
            data = np.array(df)
        # plot
        if len(average) != len(data[:,feature]):
            average = np.zeros(len(data[:,feature]))
        average = np.add(average, data[:,feature])
        plt.plot(data[:,0],data[:,feature], linestyle='--', marker=m, color=c, label=l)
    plt.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')
    plt.xlabel(xlabel)
    plt.grid(axis='y')
    plt.savefig(fileName, dpi=300)

    plt.figure(figsize=(width,height))
    plt.title(titleAvg)
    
    average = np.true_divide(average, len(list_of_files))
    

    plt.plot(data[:,0], average, linestyle='--', marker='d', color='violet', label='average')
    plt.xlabel(xlabel)
    plt.grid(axis='y')
    plt.savefig(fileNameAvg, dpi=300)

def draw_fidelity(list_of_files, label):
    title = args.titleName+' fidelity'
    titleAvg = args.titleName+' fidelity'
    feature = 5
    if args.ifcrosstalk:
        feature += 1
    xlabel = 'device'
    fileName = 'fig/' + args.titleName + '_f' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_f' + file_type
    draw_normal(title, titleAvg, list_of_files, label, feature, xlabel, fileName, fileNameAvg)

def draw_fidelity_rankCost(list_of_files, label):
    title = args.titleName+' fidelity'
    titleAvg = args.titleName+' fidelity'
    feature = 5
    if args.ifcrosstalk:
        feature += 1
    xlabel = 'device'
    fileName = 'fig/' + args.titleName + '_f_rankCost' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_f_rankCost' + file_type
    draw_normal(title, titleAvg, list_of_files, label, feature, xlabel, fileName, fileNameAvg, True)

def draw_fidelity_rankCost_group(list_of_files, label):
    title = args.titleName+' fidelity'
    titleAvg = args.titleName+' average fidelity'
    feature = 'fidelity'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_f_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_f_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_fidelity_ct_rankCost_group(list_of_files, label):
    title = args.titleName+' fidelity'
    titleAvg = args.titleName+' average fidelity'
    feature = 'fidelity_ct'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_f_rankCost_crosstalk_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_f_rankCost_crosstalk_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_fidelity_avg(list_of_files, label):
    title = args.titleName+' fidelity'
    titleAvg = args.titleName+' average fidelity'
    feature = 'fidelity'
    group = 'device'
    fileName = 'fig/' + args.titleName + '_f_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_f_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_f_improve_r_rankCost_group(list_of_files,label):
    title = args.titleName+' ratio of fidelity improvement'
    titleAvg = args.titleName+' average ratio of fidelity improvement'
    feature = 'f_improve_r'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_rfi_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_rfi_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_fct_improve_r_rankCost_group(list_of_files,label):
    title = args.titleName+' ratio of fidelity improvement'
    titleAvg = args.titleName+' average ratio of fidelity improvement'
    feature = 'fct_improve_r'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_rfi_ct_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_rfi_ct_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_cost_fidelity(list_of_files, label):
    title = args.titleName+' cost-scaled fidelity'
    titleAvg = args.titleName+' average cost-scaled fidelity'
    feature = 7
    if args.ifcrosstalk:
        feature += 1
    xlabel = 'device'
    fileName = 'fig/' + args.titleName + '_cf' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_cf' + file_type
    draw_normal(title, titleAvg, list_of_files, label, feature, xlabel, fileName, fileNameAvg)
    
def draw_cost_fidelity_rankCost(list_of_files, label):
    title = args.titleName+' cost-scaled fidelity'
    titleAvg = args.titleName+' average cost-scaled fidelity'
    feature = 7
    if args.ifcrosstalk:
        feature += 1
    xlabel = 'device'
    fileName = 'fig/' + args.titleName + '_cf_rankCost' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_cf_rankCost' + file_type
    draw_normal(title, titleAvg, list_of_files, label, feature, xlabel, fileName, fileNameAvg, True)

def draw_cost_fidelity_rankCost_group(list_of_files,label):
    title = args.titleName+' cost-scaled fidelity'
    titleAvg = args.titleName+' average cost-scaled fidelity'
    feature = 'cost-scaled fidelity'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_cf_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_cf_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_cost_fidelity_ct_rankCost_group(list_of_files,label):
    title = args.titleName+' cost-scaled fidelity'
    titleAvg = args.titleName+' average cost-scaled fidelity'
    feature = 'cost-scaled fidelity_ct'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_cf_rankCost_crosstalk_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_cf_rankCost_crosstalk_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_cost_fidelity_ct(list_of_files, label):
    title = args.titleName+' cost-scaled fidelity'
    titleAvg = args.titleName+' average cost-scaled fidelity'
    feature = 9
    xlabel = 'device'
    fileName = 'fig/' + args.titleName + '_cf' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_cf' + file_type
    draw_normal(title, titleAvg, list_of_files, label, feature, xlabel, fileName, fileNameAvg)

def draw_fidelity_dec_rankCost_group(list_of_files,label):
    title = args.titleName+' fidelity decrease ratio'
    titleAvg = args.titleName+' average fidelity decrease ratio'
    feature = 'fidelity_dec_ratio'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_fidelity_dec_ratio_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_fidelity_dec_ratio_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_g2(list_of_files, label):
    title = args.titleName+' g2'
    titleAvg = args.titleName+' average g2'
    feature = 4
    xlabel = 'device'
    fileName = 'fig/' + args.titleName + '_g2' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_g2' + file_type
    draw_normal(title, titleAvg, list_of_files, label, feature, xlabel, fileName, fileNameAvg)

def draw_g2_rankCost(list_of_files,label):
    title = args.titleName+' g2'
    titleAvg = args.titleName+' average g2'
    feature = 4
    xlabel = 'device'
    fileName = 'fig/' + args.titleName + '_g2_rankCost' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_g2_rankCost' + file_type
    draw_normal(title, titleAvg, list_of_files, label, feature, xlabel, fileName, fileNameAvg, True)

def draw_g2_rankCost_group(list_of_files, label):
    title = args.titleName+' g2'
    titleAvg = args.titleName+' average g2'
    feature = 'g2'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_g2_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_g2_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_g1_rankCost_group(list_of_files, label):
    title = args.titleName+' g1'
    titleAvg = args.titleName+' average g1'
    feature = 'g1'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_g1_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_g1_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_D(list_of_files, label):
    title = args.titleName+' depth'
    titleAvg = args.titleName+' average depth'
    feature = 2
    xlabel = 'device'
    fileName = 'fig/' + args.titleName + '_depth' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_depth' + file_type
    draw_normal(title, titleAvg, list_of_files, label, feature, xlabel, fileName, fileNameAvg)

def draw_D_rankCost(list_of_files, label):
    title = args.titleName+' depth'
    titleAvg = args.titleName+' average depth'
    feature = 2
    xlabel = 'device'
    fileName = 'fig/' + args.titleName + '_depth_rankCost' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_depth_rankCost' + file_type
    draw_normal(title, titleAvg, list_of_files, label, feature, xlabel, fileName, fileNameAvg, True)

def draw_D_rankCost_group(list_of_files,label):
    title = args.titleName+' depth'
    titleAvg = args.titleName+' average depth'
    feature = 'D'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_depth_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_depth_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def draw_ct_rankCost_group(list_of_files,label):
    title = args.titleName+' number of crosstalk gates'
    titleAvg = args.titleName+' average number of crosstalk gates'
    feature = 'crosstalk'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_ct_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_ct_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)


def draw_ctr_rankCost_group(list_of_files,label):
    title = args.titleName+' ratio of crosstalk gates'
    titleAvg = args.titleName+' average ratio of crosstalk gates'
    feature = 'ct_ratio'
    group = 'cost'
    fileName = 'fig/' + args.titleName + '_ctr_rankCost_gp' + file_type
    fileNameAvg = 'fig/' + args.titleName + '_avg_ctr_rankCost_gp' + file_type
    draw_groupBy(title, titleAvg, list_of_files, label, group, feature, group, fileName, fileNameAvg)

def analysis_fidelity(list_of_files):
    csvName = 'ana/' + args.csv.split('/')[1] + '.csv'
    # fp = open(fileName, "w")
    dfw = pd.DataFrame()
    for file in list_of_files:
        df = pd.read_csv(file)
        data = np.array(df)
        dictTmp = { "case" : 1,
                    "the std fidelity of designs" : round(np.std(data[:,5]),2),
                    "the mean fidelity of designs" : round(np.mean(data[:,5]),2),
                    "the difference of fidelity over designs" : round((np.max(data[:,5]) - np.min(data[:,5])),2),
                    "the difference between max fidelity and mean fidelity" : round((np.max(data[:,5]) - np.mean(data[:,5])),2),
                    "the difference between min fidelity and mean fidelity" : round((np.mean(data[:,5]) - np.min(data[:,5])),2),
                    "the ratio between max fidelity and mean fidelity" : round(((np.max(data[:,5]) - np.mean(data[:,5]))/np.mean(data[:,5])*100.0),2),
                    "the ratio between min fidelity and mean fidelity" : round(((np.min(data[:,5]) - np.mean(data[:,5]))/np.mean(data[:,5])*100.0),2),
                    "the ratio between max fidelity and min fidelity" : round(((np.max(data[:,5]) - np.min(data[:,5]))/np.min(data[:,5])*100.0),2)}
        try:
            dictTmp["case"] = int((re.split('-',re.split('_|/',file)[-2])[0]))
        except ValueError:
            dictTmp["case"] = re.split('_|/',file)[-2]

        dfw = dfw.append(dictTmp,  ignore_index = True)
    
    # fp.close()
    sorted_df = dfw.sort_values(by=['case'])
    # sorted_df = sorted_df.round(4)
    sorted_df.T.to_csv(csvName, index=True)

def analysis_cfct(list_of_files):
    average = np.zeros(num_device)
    for file in list_of_files:
        df = pd.read_csv(file)
        data = np.array(df)
        average += data[:,10]/data[0,10]
        curValue = data[:,10]/data[0,10]
        device_ind = np.argsort(curValue)
        print(file)
        for i in range(20):
            print("the ",i," best device is ", device_ind[num_device-i-1], " with cfct ", curValue[device_ind[num_device-i-1]])

def analysis_cf(list_of_files):
    average = np.zeros(num_device)
    for file in list_of_files:
        df = pd.read_csv(file)
        data = np.array(df)
        average += data[:,8]/data[0,8]
        
    average /= len(list_of_files)
    device_ind = np.argsort(average)
    for i in range(20):
        print("the ",i," best device is ", device_ind[num_device-i-1], " with cf ", average[device_ind[num_device-i-1]])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("csv", metavar='csv', type=str,
        help="CSV file")
    parser.add_argument("benchmark", metavar='B', type=str,
        help="Benchmark Set: arith or qaoa or QCNN")
    parser.add_argument("titleName", metavar='t', type=str,
        help="Title prefix for figure")
    parser.add_argument("--device", dest="ifdevice", action='store_true',
        help="if you want to draw curve sorted by the index of device")
    parser.add_argument("--comp", dest="ifcomp", action='store_true',
        help="use to comparison")
    parser.add_argument("--crosstalk", dest="ifcrosstalk", action='store_true',
        help="if you want to consider crosstalk effect")
    parser.add_argument("--avg", dest="ifTBavg", action='store_true',
        help="use to calculate the average of the qcnn circuit")
    # Read arguments from command line
    args = parser.parse_args()

    label, list_of_files = get_list_of_json_files()
    if args.ifTBavg == True:
        draw_fidelity_avg(list_of_files,label)
    elif args.ifdevice == True:
        draw_fidelity(list_of_files,label)
        if args.benchmark == "qcnn" or args.benchmark == "QCNN" or args.benchmark == "qaoa":
            draw_f_improve_r(list_of_files,label)
        # draw_cost_fidelity(list_of_files,label)
        draw_g2(list_of_files,label)
        draw_D(list_of_files,label)
    else:
        if args.ifcomp == True:
            width = 8
        # draw_fidelity_rankCost(list_of_files,label)
        if args.ifcrosstalk:
            draw_fidelity_ct_rankCost_group(list_of_files,label)
            draw_cost_fidelity_ct_rankCost_group(list_of_files,label)
            draw_fidelity_dec_rankCost_group(list_of_files,label)
            draw_ct_rankCost_group(list_of_files,label)
            draw_ctr_rankCost_group(list_of_files,label)
            draw_fct_improve_r_rankCost_group(list_of_files,label)
            analysis_cfct(list_of_files)
        else:
            draw_fidelity_rankCost_group(list_of_files,label)
        # draw_cost_fidelity_rankCost(list_of_files,label)
            draw_cost_fidelity_rankCost_group(list_of_files,label)
        # draw_g2_rankCost(list_of_files)
            draw_g2_rankCost_group(list_of_files,label)
            draw_g1_rankCost_group(list_of_files,label)
        # draw_D_rankCost(list_of_files)
            draw_D_rankCost_group(list_of_files,label)
            analysis_cf(list_of_files)

        # if not args.ifcrosstalk:
            draw_f_improve_r_rankCost_group(list_of_files,label)
    # if not args.ifcrosstalk:
    #     analysis_fidelity(list_of_files)


