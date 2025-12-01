# Multi-Bluetooth-Beacon-Localization
Code for Indoor Localization Using Multi-Bluetooth Beacon Deployment in a Sparse Edge Computing Environment  - Digital Twins and Applications 2025 January; 2 (1): p. e70001. https://doi.org/10.1049/dgt2.70001


# Indoor Localization from BLE Beacons

This repository provides a set of Python functions for performing **indoor localization** using BLE (Bluetooth Low Energy) data collected from multiple Raspberry Pi beacons. The pipeline loads and aggregates BLE scans, estimates distance based on RSSI, triangulates user position, smooths the trajectory, and maps coordinates to room labels on a predefined floorplan.

---

## Table of Contents

- [Dependencies](#dependencies)  
- [Data Requirements](#data-requirements)  
- [Workflow Overview](#workflow-overview)  
- [Function Reference](#function-reference)  
  - [loadBT](#loadbtdir)  
  - [computeDistance](#computedistancestartpoint-endpoint)  
  - [getSideFromRadius](#getsideradiusradius)  
  - [getRoom](#getroomloc)  
  - [locator](#locatorble_datasetimeetime)  
- [Example Usage](#example-usage)  
- [Assumptions and Limitations](#assumptions-and-limitations)

---

## Dependencies

Install required packages:

```bash
pip install numpy pandas matplotlib seaborn scipy opencv-python
