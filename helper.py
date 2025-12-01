import matplotlib.dates as dates
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import datetime
import math
import time
import cv2
import os

from scipy.interpolate import interp1d
from itertools import permutations
from IPython.display import HTML
from glob import glob




def loadBT(dir):

    dfs = pd.DataFrame()
    filenames = [file
                 for path, subdir, files in os.walk(dir)
                 for file in glob(os.path.join(path, "*.txt"))]

#     print(filenames)

    if len(filenames)==0:
        print("No data in " + dir)

    for fname in filenames:

        print(fname)
        pi_name = fname.split('/')[5][2:5]
        data = pd.read_csv(fname,sep=',',header=None, names=["Time","ID","RSSI"])
        data["PI"] = pi_name
        dfs = pd.concat([dfs,data],axis=0, ignore_index=True)

    dfs = dfs.reset_index(drop=True)
    dfs_sorted = dfs.sort_values(dfs.columns[0], ascending = True)
    dfs_sorted = dfs_sorted.reset_index(drop=True)

    return dfs_sorted




def computeDistance(startPoint, endPoint):
    return np.sqrt(((startPoint[0]-endPoint[0])**2)+((startPoint[1]-endPoint[1])**2))

def getSideFromRadius(Radius):

#     scale_factor = 1144/33.4772
    scale_factor = (955 - 130)/33.4772
    # 2m is the approximated distance of waist to drop ceiling for all participants.
    # 1144/33.4772 was emprically found to convert distances in real world to pixel distances.
    # It is function of input image/map resoloution.

    ceilingToWaist = 2 * scale_factor

    return int(np.sqrt(np.abs((Radius**2)-(ceilingToWaist**2))))



def getRoom(Loc):

    x=Loc[0]
    y=Loc[1]

    if 350 < x < 430 and 310 < y < 920:
        room = 'Activity Studio'

    elif 620 < x < 670 and 200 < y < 950:
        room = 'LC'

    elif 1060 < x < 1260 and 200 < y < 950:
        room = 'RC'

    elif 600 < x < 1210 and 130 < y < 200:
        room = 'Kitchen'

    elif 700 < x < 1100 and 680 < y < 800:
        room='Lounge'

    elif 1400 < x < 1480 and 320 < y < 730:
        room='Staff Zone'

    else:
        room='Transition Zones'

    return room




def locator(BLE_DATA,date,sTime,eTime):

    import datetime
    # You need to pass a csv file into the form of Time (timestamp form), ID, RSSi and PI value into the locator function
    # The locator function returns a dataframe with location, rooms and the time at that location

    BLE_DATA = pd.read_csv(BLE_DATA + '.csv')
    # The selected hyeprparameters are as follows based on our grid search optimization technique

    # startTime = BLE_DATA['Time'].tolist()[0]
    # endTime = BLE_DATA['Time'].tolist()[-1]

    startTime = datetime.datetime(int(date.split("/")[0]), int(date.split("/")[1]), int(date.split("/")[2]), int(sTime.split(":")[0]), int(sTime.split(":")[1]), int(sTime.split(":")[2])).timestamp()
    endTime = datetime.datetime(int(date.split("/")[0]), int(date.split("/")[1]), int(date.split("/")[2]), int(eTime.split(":")[0]), int(eTime.split(":")[1]), int(eTime.split(":")[2])).timestamp()




    directory = '/opt/scratchspace/SSAGHAF/'
    # Loading Pi X and Y Locations on Map
    locations = np.loadtxt('PiLocations.csv', delimiter = ',', dtype = {'names': ('Pi', 'X', 'Y'),'formats': ('i','i','i')}, skiprows = 1)
    Locations = {}

    for location in locations:
        Locations[location[0]] = (location[1], location[2])


    tframe = 1         # 5s was selected as the window length ########################################################################
    RHSI_METHOD = 1    # RHSI-Edge == 1 and RHSI-Agg == 0    ########################################################################
    SS = 1             # Slide = 1 and Step = 2              ########################################################################

    nextp = startTime + tframe
    sTime = startTime
    location = []
    Time_loc = []
    rooms = []
    path_x = []
    path_y = []
    HITPI_IDs = []
    NUM_HITS = []

    NPT = []
    NHT = []

    scale_factor = (955 - 130)/33.4772

    while nextp <= endTime:

        temp = BLE_DATA[(BLE_DATA['Time'] >= sTime) & (BLE_DATA['Time'] <= nextp)]

        # Choose the moving type to be slide(1)/step(2)

        # The best method based on the hyperparameter tuning was the step method so we can put SS = 2
        # Also the best weight set was S6 which is provided below

        W = [0.6, 0.4, 0.0]
        w1, w2, w3  = W[0], W[1], W[2]

        if SS == 1:

            sTime = sTime + 1
            nextp = sTime + tframe

        else:

            sTime = sTime + tframe
            nextp = nextp + tframe


        numberOfCircles = 0
        radii = []
        RADIUSINM = []

        HitPiIDs,NumOfHits = np.unique(temp['PI'],return_counts=True)

#         print(HitPiIDs)
#         len(HitPiIDs)

        N = 3.5   # N = 3.5 is a function of environment (Hyperparameter)

        NP = len(HitPiIDs) # number of Pi's

        if NP == 0:
            NH = 0 # max number of hits
        else:
            NH = np.max(NumOfHits)

        for PiID in HitPiIDs:

            RSSI = temp[temp['PI']==PiID].RSSI.mean()
            radiusInM = 10 ** ((-73 - RSSI)/(10 * N)) # You hard code the M1RSSI into -73dbm

            if radiusInM > 10:
                radiusInM = 10

            RADIUSINM.append(radiusInM)
            radii.append(getSideFromRadius(int(radiusInM * scale_factor)))

        radii = np.array(radii)


        if len(HitPiIDs) == 0:

            center_coordinates = (np.nan, np.nan) #(1160,405) modified to nan - it does not make sense to initialize randomly when there is no information

        if len(HitPiIDs) == 1:

            Pi = int(PiID)
            X, Y = Locations[Pi]
            center_coordinates = (int(X * 1830/2432), int(Y * 1167/1632))
            radius = radii[0]

        if len(HitPiIDs) > 1:

            perm = permutations(range(0,len(HitPiIDs)), 2)
            perm = list(perm)
            estimatedLocation = np.zeros((len(perm),2))
            weight = np.zeros(len(perm))


            # Method 1 -- RHSI-Agg: Method number: 0

            if RHSI_METHOD == 0:

                for n in range(0,len(perm)):

                    Pi1 = int(HitPiIDs[perm[n][0]])
                    Pi2 = int(HitPiIDs[perm[n][1]])
                    X1, Y1 = Locations[Pi1][0] * 1830/2432, Locations[Pi1][1] * 1167/1632
                    X2, Y2 = Locations[Pi2][0] * 1830/2432, Locations[Pi2][1] * 1167/1632
                    r1 = radii[perm[n][0]]
                    r2 = radii[perm[n][1]]

                    estimatedLocation[n,:] = [int(X1+(r1/(r1+r2))*(X2-X1)), int(Y1+(r1/(r1+r2))*(Y2-Y1))]
                    weight[n] = NumOfHits[perm[n][0]] + NumOfHits[perm[n][1]]

                weighted_loc = estimatedLocation * weight[:,None]
                weighted_sum_x = np.sum(weighted_loc[:,0]) / np.sum(weight)
                weighted_sum_y = np.sum(weighted_loc[:,1]) / np.sum(weight)
                center_coordinates = (int(weighted_sum_x), int(weighted_sum_y))
                radius = int(1.5 * scale_factor)


            # Method 2 -- RHSI-Edge: Method number: 1
            else:

                for n in range(0,len(perm)):

                    Pi1 = int(HitPiIDs[perm[n][0]])
                    Pi2 = int(HitPiIDs[perm[n][1]])
                    X1, Y1 = Locations[Pi1][0] * 1830/2432, Locations[Pi1][1] * 1167/1632
                    X2, Y2 = Locations[Pi2][0] * 1830/2432, Locations[Pi2][1] * 1167/1632

                    weight[n] = NumOfHits[perm[n][0]] + NumOfHits[perm[n][1]]
                    r1 = getSideFromRadius(int(RADIUSINM[perm[n][0]] * NumOfHits[perm[n][0]]/weight[n] * scale_factor))
                    r2 = getSideFromRadius(int(RADIUSINM[perm[n][1]] * NumOfHits[perm[n][1]]/weight[n] * scale_factor))


                    estimatedLocation[n,:] = [int(X1+(r1/(r1+r2))*(X2-X1)), int(Y1+(r1/(r1+r2))*(Y2-Y1))]

                weighted_loc = estimatedLocation
                weighted_sum_x = np.sum(weighted_loc[:,0]) / len(weighted_loc[:,0])
                weighted_sum_y = np.sum(weighted_loc[:,1]) / len(weighted_loc[:,1])
                center_coordinates = (int(weighted_sum_x), int(weighted_sum_y))
                radius = int(1.5 * scale_factor)


        if np.isnan(center_coordinates[0]) == False and np.isnan(center_coordinates[1]) == False:

            if len(location) >= 2:

                if computeDistance((location[-1][0], location[-1][1]), (location[-2][0], location[-2][1]))!=0:

                    x_MA = w1*center_coordinates[0] + w2*location[-1][0] + w3*location[-2][0]
                    y_MA = w1*center_coordinates[1] + w2*location[-1][1] + w3*location[-2][1]
                    center_coordinates = (x_MA, y_MA)



            location.append(center_coordinates)
            rooms.append(getRoom(center_coordinates))
            Time_loc.append(int(nextp))
            HITPI_IDs.append(HitPiIDs)
            NUM_HITS.append(NumOfHits)

        else:

            if len(location) >= 2:

                location.append(location[-1])
                rooms.append(rooms[-1])
                Time_loc.append(Time_loc[-1] + 1)
                HITPI_IDs.append(HITPI_IDs[-1])
                NUM_HITS.append(NUM_HITS[-1])



        data = {'location': location, 'rooms': rooms, 'time': Time_loc, 'PI': HITPI_IDs, '#Hits': NUM_HITS}
        dataframe = pd.DataFrame(data)

    return dataframe
