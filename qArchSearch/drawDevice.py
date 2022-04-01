# import matplotlib.pyplot as plt
import cv2
import numpy as np

def get_char_graph(coupling:list):
    # draw a character graph of the coupling graph
    char_graph = list()
    char_graph.append("00--01--02--03")

    tmp = "| "
    if (( 0, 5)     in coupling) and (( 1, 4) not in coupling):
        tmp += "\\"
    if (( 0, 5) not in coupling) and (( 1, 4)     in coupling):
        tmp += "/"
    if (( 0, 5)     in coupling) and (( 1, 4)     in coupling):
        tmp += "X"
    if (( 0, 5) not in coupling) and (( 1, 4) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 1, 6)     in coupling) and (( 2, 5) not in coupling):
        tmp += "\\"
    if (( 1, 6) not in coupling) and (( 2, 5)     in coupling):
        tmp += "/"
    if (( 1, 6)     in coupling) and (( 2, 5)     in coupling):
        tmp += "X"
    if (( 1, 6) not in coupling) and (( 2, 5) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 2, 7)     in coupling) and (( 3, 6) not in coupling):
        tmp += "\\"
    if (( 2, 7) not in coupling) and (( 3, 6)     in coupling):
        tmp += "/"
    if (( 2, 7)     in coupling) and (( 3, 6)     in coupling):
        tmp += "X"
    if (( 2, 7) not in coupling) and (( 3, 6) not in coupling):
        tmp += " "
    tmp += " |"
    char_graph.append(tmp)
    
    char_graph.append("04--05--06--07")

    tmp = "| "
    if (( 4, 9)     in coupling) and (( 5, 8) not in coupling):
        tmp += "\\"
    if (( 4, 9) not in coupling) and (( 5, 8)     in coupling):
        tmp += "/"
    if (( 4, 9)     in coupling) and (( 5, 8)     in coupling):
        tmp += "X"
    if (( 4, 9) not in coupling) and (( 5, 8) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 5,10)     in coupling) and (( 6, 9) not in coupling):
        tmp += "\\"
    if (( 5,10) not in coupling) and (( 6, 9)     in coupling):
        tmp += "/"
    if (( 5,10)     in coupling) and (( 6, 9)     in coupling):
        tmp += "X"
    if (( 5,10) not in coupling) and (( 6, 9) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 6,11)     in coupling) and (( 7,10) not in coupling):
        tmp += "\\"
    if (( 6,11) not in coupling) and (( 7,10)     in coupling):
        tmp += "/"
    if (( 6,11)     in coupling) and (( 7,10)     in coupling):
        tmp += "X"
    if (( 6,11) not in coupling) and (( 7,10) not in coupling):
        tmp += " "
    tmp += " |"
    char_graph.append(tmp)

    char_graph.append("08--09--10--11")

    tmp = "| "
    if (( 8,13)     in coupling) and (( 9,12) not in coupling):
        tmp += "\\"
    if (( 8,13) not in coupling) and (( 9,12)     in coupling):
        tmp += "/"
    if (( 8,13)     in coupling) and (( 9,12)     in coupling):
        tmp += "X"
    if (( 8,13) not in coupling) and (( 9,12) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 9,14)     in coupling) and ((10,13) not in coupling):
        tmp += "\\"
    if (( 9,14) not in coupling) and ((10,13)     in coupling):
        tmp += "/"
    if (( 9,14)     in coupling) and ((10,13)     in coupling):
        tmp += "X"
    if (( 9,14) not in coupling) and ((10,13) not in coupling):
        tmp += " "
    tmp += " | "
    if ((10,15)     in coupling) and ((11,14) not in coupling):
        tmp += "\\"
    if ((10,15) not in coupling) and ((11,14)     in coupling):
        tmp += "/"
    if ((10,15)     in coupling) and ((11,14)     in coupling):
        tmp += "X"
    if ((10,15) not in coupling) and ((11,14) not in coupling):
        tmp += " "
    tmp += " |"
    char_graph.append(tmp)

    
    char_graph.append("12--13--14--15")

    graph = ""
    for line in char_graph:
        graph += line + "\n"
    return graph

def get_device(device: int):
    my_coupling = []
    
    tmp = device
    if tmp % 2 == 1:
        my_coupling += [(0,5), (3,6), (9,12), (10,15)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(1,4), (2,7), (8,13), (11,14)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(1,6), (10, 13)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(2,5), (9,14)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(4,9), (7,10)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(5,8), (6,11)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(5,10)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(6,9)]

    return my_coupling

# order decided by normalized cost-scaled fidelity
# deviceOrder = [16,128,160,224,80,4,132,72,32,64,68,8,136,196,96,144,40,100,24,208,148,10,12,200,152,20,176,192,88,66,48,2,84,112,140,36,228,76,129,34,65,6,1,18,212,168,116,216,130,164,104,73,194,240,69,92,134,22,56,198,70,204,146,180,232,120,28,9,108,52,44,37,193,33,82,50,17,138,97,5,0,25,202,38,74,162,156,172,184,98,161,226,42,81,210,26,201,14,102,145,133,105,142,137,21,170,197,153,101,60,124,236,90,89,169,209,154,149,85,150,86,244,166,49,248,106,3,78,165,41,214,58,114,213,220,218,234,113,230,233,229,158,225,178,177,67,94,77,141,217,13,131,122,205,206,30,157,19,83,46,45,181,174,7,110,121,252,93,53,54,118,109,117,188,173,29,182,57,139,71,11,186,185,35,15,246,238,221,147,222,135,163,27,62,99,237,242,43,250,245,249,103,190,215,39,75,195,151,179,167,235,199,91,126,143,227,189,171,87,241,107,79,219,23,155,61,203,125,231,254,211,115,253,59,251,243,119,51,111,47,207,183,187,95,123,247,159,31,175,191,55,223,239,255,127,63]
# # Filename
# filename = '/Users/wanhsuan/Desktop/Github/qarcheva/fig/deviceSort/cfr_sort.jpg'

# order decided by fidelity improvement ratio
# deviceOrder = [191,255,251,215,235,158,247,94,22,219,214,198,58,10,231,122,254,119,15,103,246,116,190,238,111,157,213,183,127,83,218,151,234,102,179,187,221,181,167,230,222,174,37,105,142,110,50,121,170,95,233,91,229,123,223,224,159,93,27,153,101,118,239,253,126,143,109,62,25,237,117,124,90,189,100,89,202,169,38,173,154,149,182,85,171,43,175,73,150,86,166,139,71,217,87,69,107,59,79,228,92,106,186,134,78,34,148,155,165,125,185,250,70,243,226,42,245,249,6,146,180,18,212,196,114,205,152,47,115,210,39,206,207,120,30,19,108,176,216,26,201,14,46,45,147,113,88,135,7,163,66,63,252,82,21,199,197,138,53,54,84,97,160,31,227,99,40,60,178,236,177,29,67,209,80,77,57,74,141,55,112,24,140,244,162,23,156,208,172,194,11,240,132,72,49,248,68,184,61,203,3,98,16,41,76,56,129,65,161,131,211,136,35,204,12,232,81,75,200,96,28,9,220,52,20,168,44,130,164,145,133,193,33,137,104,144,48,17,225,2,5,188,242,13,4,32,36,51,8,195,1,128,241,64,192,0]
# filename = '/Users/wanhsuan/Desktop/Github/qarcheva/fig/deviceSort/fr_sort.jpg'

# origin order
deviceOrder = np.arange(start=0, stop=256, step=1)
filename = 'fig/deviceSort/qcnn5.jpg'



nWidth = 25
nHeigth = 11

times = 2

singleWidth = 72*times

width = singleWidth*nWidth
height = singleWidth*nHeigth

unitLength = 14*times
lineLength = 3*unitLength
space = 8*times

lineThick = 2

font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.8
fontThick = 2

img = np.full([height,width,1], 255, dtype=np.uint8)

d_list = [64, 20, 212, 88, 20]
# for i in range(256):
for i in d_list:
    startX = singleWidth*(i%nWidth) + space
    startY = singleWidth*(i//nWidth) + space
    # print("(",startX,", ",startY,")")
    # row lines
    curY = startY
    for j in range(4):
        img = cv2.line(img, (startX,curY), (startX+lineLength,curY), (0,0,255), lineThick)
        curY += unitLength
    # col lines
    curX = startX
    for j in range(4):
        img = cv2.line(img, (curX,startY), (curX,startY+lineLength), (0,0,255), lineThick)
        curX += unitLength
    
    # draw additional lines for each device
    couplingGraph = get_device(deviceOrder[i])
    for pos in couplingGraph:
        y1 = pos[0]//4
        y2 = pos[1]//4
        x1 = pos[0]%4
        x2 = pos[1]%4
        img = cv2.line(img, (startX+x1*unitLength,startY+y1*unitLength), (startX+x2*unitLength,startY+y2*unitLength), (0,0,255), lineThick)

    # plot text
    if deviceOrder[i]<=10:
        img = cv2.putText(img, str(deviceOrder[i]), (int(startX+unitLength+4),int(startY+lineLength+space+10)), font, fontScale, (0,0,255), fontThick, cv2.LINE_AA)
    elif deviceOrder[i]>=100:
        img = cv2.putText(img, str(deviceOrder[i]), (int(startX+unitLength-9),int(startY+lineLength+space+10)), font, fontScale, (0,0,255), fontThick, cv2.LINE_AA)
    else:
        img = cv2.putText(img, str(deviceOrder[i]), (int(startX+unitLength-2),int(startY+lineLength+space+10)), font, fontScale, (0,0,255), fontThick, cv2.LINE_AA)
# cv2.imshow('image', img)

cv2.waitKey(0)
cv2.destroyAllWindows()
  
# Saving the image
cv2.imwrite(filename, img)
