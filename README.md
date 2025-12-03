# Multi-Bluetooth-Beacon-Localization
When using this code, or derivatives of this code (under the BSD3 license terms), please cite:
Saghafi S, Kiarashi Y, Rodriguez AD, Levey AI, Kwon H, Clifford GD. Indoor Localization Using Multi-Bluetooth Beacon Deployment in a Sparse Edge Computing Environment. Digit Twins Appl. 2025 Jan-Dec;2(1):e70001. doi: 10.1049/dgt2.70001. Epub 2025 Mar 7. PMID: 40735132; PMCID: PMC12305822.

An open access versions of the article can be found 
here: https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/dgt2.70001  
and here: https://pmc.ncbi.nlm.nih.gov/articles/PMC12305822/

Abstract describing the research relevant to the code: Bluetooth low energy (BLE)-based indoor localization has been extensively researched due to its cost-effectiveness, low power consumption, and ubiquity. Despite these advantages, the variability of received signal strength indicator (RSSI) measurements, influenced by physical obstacles, human presence, and electronic interference, poses a significant challenge to accurate localization. In this work, we present an optimised method to enhance indoor localization accuracy by utilising multiple BLE beacons in a radio frequency (RF)-dense modern building environment. Through a proof-of-concept study, we demonstrate that using three BLE beacons reduces localization error from a worst-case distance of 9.09-2.94 m, whereas additional beacons offer minimal incremental benefit in such settings. 

The notebook `Multi_BLE.ipynb` reproduces all figures and analyses presented in the above research article.

---

### 1️⃣ Main script section for `Multi_BLE.ipynb`

```markdown
## **Main Script: Multi_BLE.ipynb**

The primary notebook for running the full localization pipeline and reproducing the figures used in the paper is:

This notebook serves as the main entry point for:

- Loading and preprocessing raw BLE data  
- Running the localization pipeline using the functions defined in this repository  
- Visualizing intermediate steps, including:  
  - RSSI distributions  
  - Estimated radii and triangulated coordinates  
  - Movement trajectories on the floorplan  
  - Room-level occupancy timelines  
- Reproducing the figures presented in the associated manuscript  

The notebook is organized into sequential sections:

1. **Imports and setup**  
2. **Loading BLE `.txt` files and building a unified dataset**  
3. **Running `locator()` across selected time intervals**  
4. **Trajectory and room occupancy visualizations**  
5. **Generation of paper-ready plots**

To reproduce the results and figures, open `Multi_BLE.ipynb` in Jupyter (or VS Code / JupyterLab) and run all cells from top to bottom.
```

---

### 2️⃣ Licensing / BSD3 compatibility note

```markdown
## **Licensing and Dependency Compatibility**

This repository is intended to be distributed under a BSD 3-Clause–compatible license.

Before releasing or redistributing this code, please verify that **all third-party libraries and dependencies used in this project are compatible with the BSD 3-Clause license**. If any dependency is not BSD3-compatible (or compatible with the chosen license), you should either:

- Replace or remove the incompatible dependency, **or**  
- Change the project’s license to one that is compatible with all dependencies.

It is the responsibility of maintainers to ensure that the final combination of project code and dependencies complies with the selected license.
```

---

## **helper.py script**

This repository provides Python functions for performing **indoor localization** using BLE (Bluetooth Low Energy) data collected from multiple Raspberry Pi beacons. The workflow loads BLE scans, estimates distance from RSSI, triangulates user position, smooths trajectories, and maps coordinates to room labels on a predefined floorplan.

---

### **Table of Contents**

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

### **Dependencies**

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

### **Data Requirements**

#### **1. BLE Text Files**

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

#### **2. Combined CSV for Localization**

The `locator` function expects a **single CSV file** (passed without `.csv` extension) containing:

```
Time, ID, RSSI, PI
```

This CSV is typically produced by saving the output of `loadBT`.

---

#### **3. PiLocations.csv**

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

### **Workflow Overview**

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

### **Function Reference**

#### **loadBT(dir)**

Loads and concatenates BLE `.txt` files from a directory (recursive).

**Output:**
A time-sorted DataFrame with columns:

```
Time, ID, RSSI, PI
```

---

#### **computeDistance(startPoint, endPoint)**

Computes Euclidean distance between two `(x, y)` coordinates:

```
sqrt((x1 - x2)² + (y1 - y2)²)
```

---

#### **getSideFromRadius(Radius)**

Converts a 3D radial distance into a horizontal pixel distance using:

* A predefined scale factor
* A fixed ceiling-to-waist height (~2 m)

---

#### **getRoom(Loc)**

Maps an `(x, y)` coordinate to a room label using predefined bounding boxes:

* Activity Studio
* LC
* RC
* Kitchen
* Lounge
* Staff Zone
* Transition Zones (default)

---

#### **locator(BLE_DATA, sTime, eTime)**

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

### **Example Usage**

#### Load BLE data

```python
df = loadBT("/path/to/BLE_txt_dir")
df.to_csv("BLE.csv", index=False)
```

#### Run localization

```python
date = "2024/11/30"  # required global variable

df_loc = locator("BLE", "09:00:00", "11:00:00")
print(df_loc.head())
```

---



