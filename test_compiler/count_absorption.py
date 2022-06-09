import argparse
import csv
import ast

if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("csv_file", metavar='cf', type=str,
        help="csv_file to store gate and gate spec")
    # parser.add_argument("sim_file", metavar='sf', type=str,
    #     help="Device: hh: heavy-hexagonal (IBM), grid: sqaure")
    # Read arguments from command line
    args = parser.parse_args()
    
    tmp = args.csv_file.split('/')
    sim_file = ""
    for i in range(len(tmp)-1):
        sim_file += (tmp[i] + '/')
    sim_file = sim_file + "sim/" + tmp[-1][:-4]+"_sim.csv"

    count_two_q_absorpt = []
    count_one_q_absorpt = []
    with open(args.csv_file, 'r') as r:
        print(args.csv_file)
        csvreader = csv.reader(r)
        header = []
        header = next(csvreader)
        data = dict()

        # print(header)
        
        for row in csvreader:
            # print(row[0])
            if row[0] == "normal":
                data[ast.literal_eval(row[1])] = ast.literal_eval(row[4])
    
    with open(sim_file, 'r') as r:
        print(sim_file)
        csvreader = csv.reader(r)
        header = []
        header = next(csvreader)
        data_sim = dict()

        # print(header)
        
        for row in csvreader:
            if row[1] == "normal":
                data_sim[ast.literal_eval(row[0])] = ast.literal_eval(row[4])
            # data_sim["g2"] = ast.literal_eval(row[6])
            # data_sim["#e"] = ast.literal_eval(row[0])
    
    for key in range(0,8):
        tmp_two = 0
        ori_one = 0
        # print(data[key])
        total_zz = 0
        total_swap = 0
        total_mix = 0
        for g_name_a in data[key]:
            for g_name in g_name_a:
                # print(g_name)
                if g_name == " ZZ":
                    # print("is a zz")
                    ori_one += 2
                    total_zz += 1
                elif g_name == " swap":
                    # print("is a swap")
                    ori_one += 6
                    total_swap += 1
                else:
                    # print("is a swap zz")
                    tmp_two += 2
                    ori_one += 8
                    total_mix += 1
        print(total_zz, total_swap, total_mix, data_sim[key], ori_one)
        count_two_q_absorpt.append(tmp_two)
        count_one_q_absorpt.append(ori_one - data_sim[key])
    
    print(count_one_q_absorpt)
    print(count_two_q_absorpt)

