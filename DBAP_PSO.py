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
def Encode(S):
    SE = sorted(S, reverse=True)
    SW = [SE.index(i) for i in S]
    SOLV = [0 for i in range(len(S))]
    for i in range(len(S)):
        for j in SW:
            if SW[j] == i:
                SOLV[i] = j
    return SOLV



### Decode Algorithm.
###
def Decode(S,CapPORT,EST,ETA,EFT,COST1,COST2,L,ProTIME):

    ### Decision variables
    X = [[0 for _ in range(CapPORT)] for _ in range(max(EFT)*5)]
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
def Initial_Solution(type,nParticle,nVessel):
    if type == "random01":
        for i in range(nParticle):
            S[i] = [rnd.uniform(0,1) for _ in range(nVessel)]
            SOL[i] = Encode(S[i])
    return S, SOL



### PBEST, GBEST Update Algorithm
def PGUpdate(nParticle,nVessel,pbest,gbest,TOTALCOST,P,G,S,sta,end,ber,GSTA,GEND,GBERTH):
    for i in range(nParticle):
        if TOTALCOST[i] < pbest[i]:
            pbest[i] = TOTALCOST[i]
            for v in range(nVessel):
                P[i][v] = S[i][v]
        if TOTALCOST[i] < gbest:
            gbest = TOTALCOST[i]
            GSTA = sta[i]
            GEND = end[i]
            GBERTH = ber[i]
            for v in range(nVessel):
                G[v] = S[i][v]
    return pbest, gbest, P, G, GSTA, GEND, GBERTH



### PSO Update Velocity
###
def Update_Velocity(nParticle,nVessel,S,V,P,G,w,c1,c2,Vmax):
    for i in range(nParticle):
        for v in range(nVessel):
            V[i][v] = w*V[i][v] + (rnd.uniform(0,1))*c1*(P[i][v] - S[i][v]) + (rnd.uniform(0,1))*c2*(G[v] - S[i][v])
            if V[i][v] >= Vmax:
                V[i][v] = Vmax
            elif V[i][v] <= -Vmax:
                V[i][v] = -Vmax
    return V



### PSO Update Coordinates
###
def Update_Coordinates(nParticle,nVessel,S,V):
    for i in range(nParticle):
        for v in range(nVessel):
            S[i][v] += V[i][v]
            if S[i][v] > 1:
                S[i][v] = 1
            elif S[i][v] < 0:
                S[i][v] = 0
    return S



### Mutation Phase
###
def Mutation(nParticle,nVessel,S,Ratio):
    Aux1 = np.random.permutation(nParticle)
    Aux2 = list()
    for i in range(int(round(nParticle*Ratio))):
        Aux2.append(Aux1[i])
    for i in Aux2:
        S[i] = [rnd.uniform(0,1) for _ in range(nVessel)]
    return S




### PARAMETERS
###
### DBAP Parameters
###
CapPORT = 30
nVessel = 60
ProTIME = [27,30,18,25,22,18,16,40,31,38,27,34,40,10,30,32,35,30,13,30,39,10,20,16,28,16,30,31,19,12,29,20,24,14,19,14,22,14,22,38,31,31,13,36,13,19,13,31,22,29,11,27,15,33,33,28,14,14,10,21]
EST = [7,142,96,67,1,68,10,129,33,8,7,15,137,3,118,108,94,128,112,156,24,55,21,73,144,145,81,84,40,8,26,7,39,125,1,2,143,140,144,27,103,105,1,157,113,69,63,67,99,154,32,133,66,98,102,145,5,148,10,39]
ETA = [22,163,131,101,35,79,32,164,43,31,41,28,157,42,151,132,118,156,136,192,44,75,55,87,159,162,96,102,54,36,39,37,66,158,20,21,153,166,165,48,125,140,45,190,123,93,103,94,114,167,52,152,106,137,122,169,46,170,33,50]
EFT = [ETA[i]+ProTIME[i] for i in range(nVessel)]
L = [1,3,3,2,3,2,1,3,1,1,2,2,3,2,2,2,3,2,3,2,3,1,3,3,3,3,1,3,2,3,2,2,3,2,2,3,3,2,1,3,1,2,3,2,1,3,2,2,2,1,3,3,3,3,3,2,2,3,1,3]
COST1 = [2,4,4,2,1,2,4,3,4,2,3,3,1,4,5,2,1,5,2,1,5,4,1,1,1,5,4,4,1,1,2,2,1,5,5,5,4,4,2,2,5,2,2,1,2,2,4,4,4,3,2,3,3,2,1,3,2,5,3,5]
COST2 = [3,3,4,1,5,4,4,2,5,3,3,3,3,1,5,2,3,5,2,1,4,3,5,4,3,5,3,4,3,1,4,3,4,3,2,2,3,3,5,3,3,3,5,1,2,2,4,4,2,2,2,5,3,2,1,3,4,1,4,2]
CB = [10,20]
###
### PSO Parameters
###
nGeneration = 100
nParticle   = 20
Vmax        = 0.1
w           = 0.70
c1          = 1.80
c2          = 1.80
V           = [[0.1 for _ in range(nVessel)] for _ in range(nParticle)]
P           = [[0 for _ in range(nVessel)] for _ in range(nParticle)]


ITR  = list()
CST  = list()
TIME = list()
for n in range(50):
    ITR.append(n)
    pbest       = [9999 for _ in range(nParticle)]
    gbest       = 9999
    ### VARIABLES
    ###
    ### DBAP Variables
    ###
    sta       = [[0 for _ in range(nVessel)] for _ in range(nParticle)]
    end       = [[0 for _ in range(nVessel)] for _ in range(nParticle)]
    ber       = [[0 for _ in range(nVessel)] for _ in range(nParticle)]
    COSTS     = [[0 for _ in range(nVessel)] for _ in range(nParticle)]
    TOTALCOST = [0 for _ in range(nParticle)]
    ###
    ### PSO Variables
    ###
    G   = [0 for _ in range(nVessel)]
    S   = [[0 for _ in range(nVessel)] for _ in range(nParticle)]
    SOL = [0 for _ in range(nParticle)]
    SZ  = [9999 for _ in range(nParticle)]
    GSTA = [0 for _ in range(nVessel)]
    GEND = [0 for _ in range(nVessel)]
    GBERTH = [0 for _ in range(nVessel)]
    SC1 = 0
    SC2 = 0
    ###
    ### GRAPHICS Variables
    ###
    BEST   = list()
    PBESTI = list()
    ITER   = list()



    ### Initial Solutions
    ###
    S, SOL = Initial_Solution("random01",nParticle,nVessel)



    ### Initial Decode Phase
    ###
    for i in range(nParticle):
        sta[i],end[i],ber[i] = Decode(SOL[i],CapPORT, EST, ETA, EFT,COST1,COST2, L, ProTIME)



    ### Initial Cost Calculate Phase
    ###
    for i in range(nParticle):
        for v in range(nVessel):
            COSTS[i][v] = CostCalculate(ETA[v], EFT[v], sta[i][v], end[i][v], COST1[v], COST2[v])
        TOTALCOST[i] = sum(COSTS[i])



    ### Initial pbest, gbest Update
    ###
    pbest, gbest, P, G, GSTA, GEND, GBERTH = PGUpdate(nParticle,nVessel,pbest,gbest,TOTALCOST,P,G,S,sta,end,ber,GSTA,GEND,GBERTH)



    ### Timer Start
    ###
    time1 = time.time()



    ### PSO Algorithm Start
    ###
    for j in range(nGeneration):

        V = Update_Velocity(nParticle,nVessel,S,V,P,G,w,c1,c2,Vmax)
        S = Update_Coordinates(nParticle,nVessel,S,V)

        if np.mod(j,5) == 0:
            S = Mutation(nParticle,nVessel,S,0.20)

        aux1 = 0

        for i in range(nParticle):
            SOL[i] = Encode(S[i])
            sta[i], end[i], ber[i] = Decode(SOL[i],CapPORT, EST, ETA, EFT,COST1,COST2, L, ProTIME)
            for v in range(nVessel):
                COSTS[i][v] = CostCalculate(ETA[v], EFT[v], sta[i][v], end[i][v], COST1[v], COST2[v])
            TOTALCOST[i] = sum(COSTS[i])
            if TOTALCOST[i] < gbest:
                aux1 = 1

        if aux1 == 0:
            SC2 += 1
        else:
            SC2 = 0

        if SC2 >= nGeneration*0.25:
            break

        pbest, gbest, P, G, GSTA, GEND, GBERTH = PGUpdate(nParticle,nVessel,pbest,gbest,TOTALCOST,P,G,S,sta,end,ber,GSTA,GEND,GBERTH)

        BEST.append(gbest)
        ITER.append(j+1)
        if gbest == 0:
            break
    TIME.append(time.time()-time1)
    CST.append(gbest)

print "Ortalama Sonuc   : ", np.average(CST)
print "En iyi Sonuc     : ", np.min(CST)
print "En kotu Sonuc    : ", np.max(CST)
print "Sonuclarin Std   : ", np.std(CST)
print "Ortalama Zaman   : ", np.average(TIME)
print "En iyi Zaman     : ", np.min(TIME)
print "En kotu Zaman    : ", np.max(TIME)
print "Zamanlarin Std   : ", np.std(TIME)

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