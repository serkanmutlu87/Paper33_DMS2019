import matplotlib
import numpy as np
import random as rnd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time



### Prevents incorrect entry (String)
###
def TakeStringInput(msg, posb):
    posbString = ", ".join(posb)
    inp = input(msg + " (" + posbString + ") = ")
    while inp not in posb:
        print("Lutfen dogru bir deger giriniz. Degerler =", posbString)
        inp = input(msg + " (" + posbString + ") = ")
    return inp



### Prevents incorrect entry (Numeric)
###
def TakeIntegerInput(msg):
    inp = input(msg + " = ")
    while not inp.isnumeric():
        print("Lutfen bir sayi giriniz.")
        inp = input(msg + " = ")
    return int(inp)



### Encode Algorithm. Sorts the list from large to small and keeps index values.
### For example;
### S    = [0.82, 0.18, 0.71, 0.53, 0.19, 0.22, 0.31, 0.44, 0.08, 0.59]
### SE   = [0.82, 0.71, 0.59, 0.53, 0.44, 0.31, 0.22, 0.19, 0.18, 0.08]
### SW   = [0, 8, 1, 3, 7, 6, 5, 4, 9, 2]
### SOLV = [0, 2, 9, 3, 7, 6, 5, 4, 1, 8]
###
def Encode(Z):
    SE = sorted(Z)
    print SE
    SW = [SE.index(i) for i in Z]
    SOLV = [0 for i in range(len(Z))]
    for i in range(len(Z)):
        for j in SW:
            if SW[j] == i:
                SOLV[i] = j
    return SOLV



### Decode Algorithm.
###
def Decode(S,CapPORT,EST,ETA,EFT,COST1,COST2,L,ProTIME):

    ### Decision variables
    X = [[0 for _ in range(CapPORT)] for _ in range(max(EFT)*4)]
    starttime = [0 for _ in range(nVessel)]
    endtime = [0 for _ in range(nVessel)]
    berthing_position = [0 for _ in range(nVessel)]

    ### Auxiliary variables
    AuxETA = [ETA[v] for v in range(nVessel)]
    Ear = [0 for _ in range(nVessel)]
    Lat = [0 for _ in range(nVessel)]

    for v in S:
        while True:
            for i in range(CapPORT):
                assign = 1

                for q in CB:
                    if i < q:
                        if i + L[v] >= q:
                            assign = 0
                            break

                ### Assignabiliy control
                for j in range(AuxETA[v] - 1, AuxETA[v] + ProTIME[v] - 1):
                    for l in range(L[v]):
                        if i+l >= CapPORT:
                            break
                        elif X[j][i+l] == 1:
                            assign = 0
                            break
                    if assign == 0:
                        break

                ### Assign or not assign
                if assign == 1:
                    starttime[v] = AuxETA[v]
                    endtime[v] = AuxETA[v] + ProTIME[v]
                    Aux1 = []
                    for l in range(L[v]):
                        Aux1.append(i + l)
                    berthing_position[v] = Aux1
                    for t in range(starttime[v] - 1, endtime[v] - 1):
                        for l in berthing_position[v]:
                            X[t][l] = 1
                    break
                elif i + L[v] >= CapPORT:
                    Lat[v] += 1
                    AuxETA[v] = ETA[v] + Lat[v]
                    break

            ### Completion of assignment
            if assign == 1:
                break

    ### Return decision variables
    return starttime, endtime, berthing_position



### Cost Calculate Algorithm
###
def CostCalculate(ETA,EFT,start,end,earcost,latecost):
    Cost = 0
    if start-ETA < 0:
        Cost += earcost*(ETA-start)
    if EFT-end < 0:
        Cost += latecost*(end-EFT)
    return Cost



### PARAMETERS
###
### DBAP Parameters
###
CapPORT = 10
nVessel = 24
ProTIME = [21,28,36,21,17,23,13,63,70,49,16,32,14,12,23,37,26,25,9,29,55,13,10,14]
EST = [26,33,32,70,75,78,113,66,68,103,134,140,118,173,200,199,205,215,231,239,266,295,296,286]
ETA = [26,33,32,70,75,78,113,92,94,103,134,152,118,173,200,199,205,215,231,239,266,295,296,286]
EFT = [ETA[i]+ProTIME[i] for i in range(nVessel)]
L = [2,2,2,2,2,2,1,1,2,3,1,2,1,1,2,2,1,1,1,2,3,1,2,1]
COST1 = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
COST2 = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
CB = [4,7]
### VARIABLES
###
### DBAP Variables
###
sta       = [0 for _ in range(nVessel)]
end       = [0 for _ in range(nVessel)]
ber       = [0 for _ in range(nVessel)]
COSTS     = [0 for _ in range(nVessel)]
TOTALCOST = 0

print len(ProTIME),len(EST),len(ETA),len(L),len(COST1),len(COST2)



### Initial Solutions
###
SOL = Encode(ETA)


### Decode Phase
###
sta,end,ber = Decode(SOL,CapPORT, EST, ETA, EFT,COST1,COST2, L, ProTIME)



### Initial Cost Calculate Phase
###
for v in range(nVessel):
    COSTS[v] = CostCalculate(ETA[v], EFT[v], sta[v], end[v], COST1[v], COST2[v])
TOTALCOST = sum(COSTS)

print TOTALCOST
print ETA
print sta
print end
print ber
print COSTS