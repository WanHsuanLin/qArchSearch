import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import json
from matplotlib.ticker import FormatStrFormatter, NullFormatter


def geomean(a):
    tmp = 1
    for it in a:
        tmp *= it
    return tmp ** (1/len(a))


file_object = open("fpqa.json")
fpqa_json = json.load(file_object)
file_object.close()

file_object = open("fpqa_proj.json")
fpqa_proj_json = json.load(file_object)
file_object.close()

file_object = open("SYC_T1F994_fid.json")
sycamore_T1F994_json = json.load(file_object)
file_object.close()

file_object = open("SYC_T1F994_fid_nodeco.json")
sycamore_T0F994_json = json.load(file_object)
file_object.close()

file_object = open("SYC_T1F100_fid.json")
sycamore_T1F100_json = json.load(file_object)
file_object.close()

file_object = open("SYC_T10F997_fid.json")
sycamore_T10F997_json = json.load(file_object)
file_object.close()

file_object = open("SYC_T10F999_fid.json")
sycamore_T10F999_json = json.load(file_object)
file_object.close()

file_object = open("SYC_T100F999_fid.json")
sycamore_T100F999_json = json.load(file_object)
file_object.close()

ticks = []
fpqa_data = []
fpqa_proj_data = []
sycamore_T1F994_data = []
sycamore_T0F994_data = []
sycamore_T1F100_data = []
sycamore_T10F997_data = []
sycamore_T10F999_data = []
sycamore_T100F999_data = []


for i in range(8, 24, 2):
    sycamore_T1F994_data.append(
        geomean([sycamore_T1F994_json[str(i)][j] for j in range(10)]))
    sycamore_T0F994_data.append(
        geomean([sycamore_T0F994_json[str(i)][j] for j in range(10)]))
    sycamore_T1F100_data.append(
        geomean([sycamore_T1F100_json[str(i)][j] for j in range(10)]))

    sycamore_T10F997_data.append(
        geomean([sycamore_T10F997_json[str(i)][j] for j in range(10)]))
    sycamore_T10F999_data.append(
        geomean([sycamore_T10F999_json[str(i)][j] for j in range(10)]))
    sycamore_T100F999_data.append(
        geomean([sycamore_T100F999_json[str(i)][j] for j in range(10)]))

    fpqa_data.append(geomean([fpqa_json[str(i)][j] for j in range(10)]))
    fpqa_proj_data.append(
        geomean([fpqa_proj_json[str(i)][j] for j in range(10)]))
    ticks.append(str(i))


font = {'family': 'serif',
        'weight': 'normal',
        'size': 11}
matplotlib.rc('font', **font)
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
# plt.rcParams["figure.figsize"] = (8.5,5)


plt.figure()


plt.plot(sycamore_T1F994_data, '.-', c='tab:orange',
         label=r'Sycamore, baseline')
# plt.plot(sycamore_T0F994_data, '+', c='tab:purple', label=r'Sycamore $T\to\infty,\ f_2=$99.4%')
# plt.plot(sycamore_T1F100_data, 'x', c='tab:green',label=r'Sycamore 1$\times T,\ f_2\to$ 100%')

# plt.plot(sycamore_T10F997_data, '^', c='tab:gray', label=r'Sycamore 10$\times T,\ f_2=$99.7%')
# plt.plot(sycamore_T10F999_data, 'o', c='tab:olive', label=r'Sycamore 10$\times T,\ f_2=$99.9%')
plt.plot(sycamore_T100F999_data, '*', c='tab:blue',
         label=r'Sycamore 100$\times T,\ f_2=$99.9%')

plt.plot(fpqa_data, '-', c='tab:red', label=r'RAA $f_2$=97.5% (current)')
plt.plot(fpqa_proj_data, '--', c='tab:pink', label=r'RAA $f_2$=99.4%')


plt.legend()

plt.xticks(range(0, len(ticks)), ticks)
# plt.yticks([0.03, 0.06, 0.10, 0.20, 0.50, 1.00])
plt.yscale('log')
# plt.grid(True, 'major', 'y')
plt.xlabel('Number of qubits in QAOA program')
plt.title('Sycamore + t|ket>  vs.  RAA + OLSQ-RAA')
ax = plt.gca()
ax.set_yscale('log')
ax.set_yticks([0.03, 0.06, 0.10, 0.20, 0.50, 1.00])
# plt.ylim(0.02, 1)
ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
ax.yaxis.set_minor_formatter(NullFormatter())
# plt.ylabel('Estimated circuit fidelity (one iteration)')

# ax = plt.gca() #you first need to get the axis handle

# define y-unit to x-unit ratio
# ratio = 0.25

# get x and y limits
# x_left, x_right = ax.get_xlim()
# y_low, y_high = ax.get_ylim()

# set aspect ratio
# ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)

plt.savefig(f"qaoa.pdf")
