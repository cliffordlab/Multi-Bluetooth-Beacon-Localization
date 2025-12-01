# Multi-Bluetooth-Beacon-Localization
Code for Indoor Localization Using Multi-Bluetooth Beacon Deployment in a Sparse Edge Computing Environment  - Digital Twins and Applications 2025 January; 2 (1): p. e70001. https://doi.org/10.1049/dgt2.70001

# **Indoor Localization from BLE Beacons -- helper.py**

This repository provides Python functions for performing **indoor localization** using BLE (Bluetooth Low Energy) data collected from multiple Raspberry Pi beacons. The workflow loads BLE scans, estimates distance from RSSI, triangulates user position, smooths trajectories, and maps coordinates to room labels on a predefined floorplan.

---

## **Table of Contents**

* [Dependencies](#dependencies)
* [Data Requirements](#data-requirements)
* [Workflow Overview](#workflow-overview)
* [Function Reference](#function-reference)

  * [loadBT](#loadbtdir)
  * [computeDistance](#computedistancestartpoint-endpoint)
  * [getSideFromRadius](#getsideradiusradius)
  * [getRoom](#getroomloc)
  * [locator](#locatorble_datasetimeetime)
* [Example Usage](#example-usage)
* [Assumptions and Limitations](#assumptions-and-limitations)

---

## **Dependencies**

Install required packages:

```
pip install numpy pandas matplotlib seaborn scipy opencv-python
```

Modules used:

* numpy
* pandas
* matplotlib
* seaborn
* scipy
* opencv-python
* glob
* itertools
* datetime
* os

---

## **Data Requirements**

### **1. BLE Text Files**

The `loadBT` function expects a directory containing `.txt` files with the format:

```
Time, ID, RSSI
```

Each file corresponds to a single Raspberry Pi beacon.
The Pi ID is extracted from the file path using:

```
pi_name = fname.split('/')[5][2:5]
```

> Adjust the indexing if your folder structure differs.

---

### **2. Combined CSV for Localization**

The `locator` function expects a **single CSV file** (passed without `.csv` extension) containing:

```
Time, ID, RSSI, PI
```

This CSV is typically produced by saving the output of `loadBT`.

---

### **3. PiLocations.csv**

A file named **PiLocations.csv** must exist in the working directory.

Format:

```
Pi,X,Y
101,500,300
102,800,700
...
```

Coordinates must match your map resolution.

---

## **Workflow Overview**

1. Load BLE `.txt` files using `loadBT()`.
2. Save the combined DataFrame to a CSV file.
3. Define the global date variable:

```
date = "YYYY/MM/DD"
```

4. Run `locator()` with:

   * BLE CSV base name (no `.csv`)
   * Start time `"HH:MM:SS"`
   * End time `"HH:MM:SS"`

5. `locator` will:

   * Slide a time window through BLE data
   * Convert RSSI to distance using a log-distance path-loss model
   * Triangulate position using RHSI-Agg or RHSI-Edge
   * Smooth the trajectory using a moving average
   * Assign room labels based on bounding boxes
   * Return a DataFrame with location, rooms, time, Pi hits, and hit counts

---

## **Function Reference**

### **loadBT(dir)**

Loads and concatenates BLE `.txt` files from a directory (recursive).

**Output:**
A time-sorted DataFrame with columns:

```
Time, ID, RSSI, PI
```

---

### **computeDistance(startPoint, endPoint)**

Computes Euclidean distance between two `(x, y)` coordinates:

```
sqrt((x1 - x2)² + (y1 - y2)²)
```

---

### **getSideFromRadius(Radius)**

Converts a 3D radial distance into a horizontal pixel distance using:

* A predefined scale factor
* A fixed ceiling-to-waist height (~2 m)

---

### **getRoom(Loc)**

Maps an `(x, y)` coordinate to a room label using predefined bounding boxes:

* Activity Studio
* LC
* RC
* Kitchen
* Lounge
* Staff Zone
* Transition Zones (default)

---

### **locator(BLE_DATA, sTime, eTime)**

Main indoor localization pipeline.

**Inputs:**

* BLE CSV base name (without `.csv`)
* Start time `"HH:MM:SS"`
* End time `"HH:MM:SS"`

**Requires global:**

```
date = "YYYY/MM/DD"
```

**Outputs:**
A DataFrame containing:

```
location   (x, y pixel coordinates)
rooms      (room labels)
time       (UNIX timestamps)
PI         (Pis detected)
#Hits      (hit counts per Pi)
```

---

## **Example Usage**

### Load BLE data

```python
df = loadBT("/path/to/BLE_txt_dir")
df.to_csv("BLE.csv", index=False)
```

### Run localization

```python
date = "2024/11/30"  # required global variable

df_loc = locator("BLE", "09:00:00", "11:00:00")
print(df_loc.head())
```

---



