# Multi-Bluetooth-Beacon-Localization
Code for Indoor Localization Using Multi-Bluetooth Beacon Deployment in a Sparse Edge Computing Environment  - Digital Twins and Applications 2025 January; 2 (1): p. e70001. https://doi.org/10.1049/dgt2.70001


Indoor Localization from BLE Beacons

This repository provides a set of Python functions to perform indoor localization using BLE (Bluetooth Low Energy) data collected from multiple Raspberry Pi beacons. The workflow involves loading BLE scans, estimating distances from RSSI, triangulating participant location, smoothing trajectories, and mapping coordinates to room labels.

Table of Contents

Dependencies

Data Requirements

Workflow Overview

Function Reference

loadBT

computeDistance

getSideFromRadius

getRoom

locator

Example Usage

Assumptions and Limitations

Dependencies

Install required packages:

pip install numpy pandas matplotlib seaborn scipy opencv-python


Modules used:

numpy  
pandas  
matplotlib  
seaborn  
scipy  
opencv-python  
glob  
itertools  
datetime  

Data Requirements
1. BLE Text Files

The loadBT function expects a directory containing .txt files with:

Time, ID, RSSI


Each file corresponds to one Pi beacon. The Pi ID is extracted from the filename structure.

2. Combined CSV for Localization

The locator function expects a CSV (passed without .csv extension) that contains:

Time, ID, RSSI, PI

3. PiLocations.csv

locator requires a file named PiLocations.csv in the working directory:

Pi,X,Y
101,500,300
102,800,700
...


Coordinates must match the map resolution used in the project.

Workflow Overview

Load BLE text data with loadBT.

Save the combined DataFrame as .csv.

Call locator with:

BLE CSV base name (no .csv)

Start and end times ("HH:MM:SS")

A global date variable in "YYYY/MM/DD" format.

locator:

Slides a time window through the BLE data.

Converts RSSI to distance using a path-loss model.

Estimates location using RHSI-Agg or RHSI-Edge.

Smooths coordinates with a moving average.

Assigns room labels via getRoom.

Returns a DataFrame with:

location

rooms

time

PI

#Hits

Function Reference
loadBT(dir)

Loads and concatenates BLE .txt files from a directory.

Input:
dir — directory containing BLE text files.

Output:
A time-sorted DataFrame with columns:

Time, ID, RSSI, PI


Pi ID is inferred from the file path.

computeDistance(startPoint, endPoint)

Computes Euclidean distance between two 2D coordinates.

Returns:
float – sqrt((x1−x2)² + (y1−y2)²)

getSideFromRadius(Radius)

Converts a 3D radial distance into a horizontal pixel distance using a predefined scale factor and ceiling-to-waist height.

Returns:
Horizontal side length in pixels.

getRoom(Loc)

Maps a 2D point (x, y) to a room label based on hard-coded bounding boxes.

Rooms include:

Activity Studio

LC

RC

Kitchen

Lounge

Staff Zone

Transition Zones (default)

locator(BLE_DATA, sTime, eTime)

Main localization pipeline.

Inputs:

BLE_DATA — base name of BLE CSV (without .csv)

sTime — "HH:MM:SS" start time

eTime — "HH:MM:SS" end time

Requires global:

date = "YYYY/MM/DD"


Process:

Loads BLE CSV.

Converts time strings + date → UNIX timestamps.

Applies sliding window (tframe = 1s).

Computes distance from RSSI using log-distance formula.

Triangulates location using RHSI-Agg or RHSI-Edge.

Smooths location with a weighted moving average.

Maps location to room name.

Builds the output DataFrame.

Returns:
A DataFrame containing:

location   (x,y pixel coordinates)
rooms      (room labels)
time       (UNIX timestamp)
PI         (list of Pis hit in window)
#Hits      (hit count per Pi)

Example Usage
Load BLE data
df = loadBT("/path/to/BLE_txt_dir")
df.to_csv("BLE_combined.csv", index=False)

Run localization
date = "2024/11/30"   # must be defined globally

df_loc = locator("BLE_combined", "09:00:00", "11:00:00")
print(df_loc.head())

