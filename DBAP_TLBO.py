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
    SE = sorted(Z, reverse=True)
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
    X = [[0 for _ in range(CapPORT)] for _ in range(max(EFT)*2)]
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
                    if AuxETA[v] < EST[v]:
                        Ear[v] = 9999
                        AuxETA[v] = ETA[v]
                        break
                    else:
                        if CostCalculate(ETA[v],EFT[v],ETA[v]-Ear[v]-1,ETA[v]-Ear[v]-1+ProTIME[v],COST1[v],COST2[v]) <= CostCalculate(ETA[v],EFT[v],ETA[v]+Lat[v]+1,ETA[v]+Lat[v]+1+ProTIME[v],COST1[v],COST2[v]):
                            Ear[v] += 1
                            AuxETA[v] = ETA[v] - Ear[v]
                            break
                        else:
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



### Initial Solution Algorithms
###
def Initial_Solution(type,nStudent,nVessel):
    if type == "random01":
        for i in range(nStudent):
            Z[i] = [rnd.uniform(0,1) for _ in range(nVessel)]
            SOL[i] = Encode(Z[i])
    elif type == "random-1+1":
        for i in range(nStudent):
            Z[i] = [rnd.uniform(-1,1) for _ in range(nVessel)]
            SOL[i] = Encode(Z[i])
    return Z, SOL



def Calculate_Zmean(nStudent,nVessel,Z):
    ZMEAN = list()
    for i in range(nVessel):
        aux1 = list()
        for j in range(nStudent):
            aux1.append(Z[j][i])
        ZMEAN.append(np.average(aux1))
    return ZMEAN



def Assign_Teacher(nStudent,nVessel,Z,TOTALCOST,sta,end,ber,ZTEACHER,best_cost,GSTA,GEND,GBERTH):
    for i in range(nStudent):
        if TOTALCOST[i] < best_cost:
            best_cost = TOTALCOST[i]
            GSTA = sta[i]
            GEND = end[i]
            GBERTH = ber[i]
            for v in range(nVessel):
                ZTEACHER[v] = Z[i][v]
    return ZTEACHER, best_cost, GSTA, GEND, GBERTH



### Mutation Phase
###
def Mutation(nStudent,nVessel,Z,Ratio):
    Aux1 = np.random.permutation(nStudent)
    Aux2 = list()
    for i in range(int(round(nStudent*Ratio))):
        Aux2.append(Aux1[i])
    for i in Aux2:
        Z[i] = [rnd.uniform(0,1) for _ in range(nVessel)]
    return Z



### Teacher Phase Algorithm
###
def Teacher_Phase(nStudent,nVessel,Z,ZTEACHER,ZMEAN):
    for i in range(nStudent):
        for v in range(nVessel):
            Z[i][v] = Z[i][v] + (rnd.uniform(0,1))*(ZTEACHER[v] - ((rnd.randint(1,2))*ZMEAN[v]))
    return Z



### Teacher Phase Algorithm
###
def Student_Phase(nStudent,nVessel,TOTALCOST,Z):
    Z2 = [[0 for _ in range(nVessel)] for _ in range(nStudent)]
    for i in range(nStudent):
        for j in range(nStudent):
            if i!= j:
                if TOTALCOST[i] <= TOTALCOST[j]:
                    for v in range(nVessel):
                        Z2[i][v] = Z[i][v] +(rnd.uniform(0,1))*(Z[i][v] - Z[j][v])
                else:
                    for v in range(nVessel):
                        Z2[i][v] = Z[i][v] +(rnd.uniform(0,1))*(Z[j][v] - Z[i][v])
    return Z2



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
###
### TLBO Parameters
###
nGeneration = 100
nStudent = 20

ITR  = list()
CST  = list()
TIME = list()
for n in range(50):
    best_cost   = 9999
    ITR.append(n)
    ### VARIABLES
    ###
    ### DBAP Variables
    ###
    sta       = [[0 for _ in range(nVessel)] for _ in range(nStudent)]
    end       = [[0 for _ in range(nVessel)] for _ in range(nStudent)]
    ber       = [[0 for _ in range(nVessel)] for _ in range(nStudent)]
    COSTS     = [[0 for _ in range(nVessel)] for _ in range(nStudent)]
    TOTALCOST = [0 for _ in range(nStudent)]
    ###
    ### TLBO Variables
    ###
    Z        = [[0 for _ in range(nVessel)] for _ in range(nStudent)]
    ZMEAN    = [0 for _ in range(nVessel)]
    ZTEACHER = [0 for _ in range(nVessel)]
    SOL      = [0 for _ in range(nStudent)]
    GSTA     = [0 for _ in range(nVessel)]
    GEND     = [0 for _ in range(nVessel)]
    GBERTH   = [0 for _ in range(nVessel)]
    SC1      = 0
    SC2      = 0
    ###
    ### GRAPHICS Variables
    ###
    BEST   = list()
    PBESTI = list()
    ITER   = list()



    ### Initial Solutions
    ###
    Z, SOL = Initial_Solution("random-1+1",nStudent,nVessel)



    ### Initial Decode Phase
    ###
    for i in range(nStudent):
        sta[i],end[i],ber[i] = Decode(SOL[i],CapPORT, EST, ETA, EFT,COST1,COST2, L, ProTIME)



    ### Initial Cost Calculate Phase
    ###
    for i in range(nStudent):
        for v in range(nVessel):
            COSTS[i][v] = CostCalculate(ETA[v], EFT[v], sta[i][v], end[i][v], COST1[v], COST2[v])
        TOTALCOST[i] = sum(COSTS[i])



    ZMEAN = Calculate_Zmean(nStudent,nVessel,Z)
    ZTEACHER, best_cost, GSTA, GEND, GBERTH = Assign_Teacher(nStudent,nVessel,Z,TOTALCOST,sta,end,ber,ZTEACHER,best_cost,GSTA,GEND,GBERTH)



    ### Timer Start
    ###
    time1 = time.time()



    ### TLBO Algorithm Start
    ###
    for j in range(nGeneration):

        Z = Teacher_Phase(nStudent,nVessel,Z,ZTEACHER,ZMEAN)
        Z = Student_Phase(nStudent,nVessel,TOTALCOST,Z)

        if np.mod(j,5) == 0:
            Z = Mutation(nStudent,nVessel,Z,0.20)

        aux1 = 0

        for i in range(nStudent):
            SOL[i] = Encode(Z[i])
            sta[i], end[i], ber[i] = Decode(SOL[i],CapPORT, EST, ETA, EFT,COST1,COST2, L, ProTIME)
            for v in range(nVessel):
                COSTS[i][v] = CostCalculate(ETA[v], EFT[v], sta[i][v], end[i][v], COST1[v], COST2[v])
            TOTALCOST[i] = sum(COSTS[i])
            if TOTALCOST[i] < best_cost:
                aux1 = 1

        if aux1 == 0:
            SC2 += 1
        else:
            SC2 = 0

        if SC2 >= nGeneration*0.25:
            break

        ZMEAN = Calculate_Zmean(nStudent,nVessel,Z)
        ZTEACHER, best_cost, GSTA, GEND, GBERTH = Assign_Teacher(nStudent,nVessel,Z,TOTALCOST,sta,end,ber,ZTEACHER,best_cost,GSTA,GEND,GBERTH)


        BEST.append(best_cost)
        ITER.append(j+1)
        if best_cost == 0:
            break
    TIME.append(time.time()-time1)
    CST.append(best_cost)

print "O.F. Mean        : ", np.average(CST)
print "Best O.F.        : ", np.min(CST)
print "Worst O.F.       : ", np.max(CST)
print "Std O.F          : ", np.std(CST)
print "Time Mean        : ", np.average(TIME)
print "Best Time        : ", np.min(TIME)
print "Worst Time       : ", np.max(TIME)
print "Std Time         : ", np.std(TIME), "\n"
print "Starting Time    : ", GSTA
print "Ending Time      : ", GEND
print "Assign Berth     : ", GBERTH

plt.subplot(1,2,1)
plt.title("Cost")
plt.xlabel('Iteration')
plt.ylabel('Values')
plt.plot(ITR,CST)
plt.subplot(1,2,2)
plt.title("Time")
plt.xlabel('Iteration')
plt.plot(ITR,TIME),("Time")
plt.show()