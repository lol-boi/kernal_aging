# Linux Kernel Software Aging Framework: Module Guide

This document provides a detailed technical breakdown of each module in the framework and how it is implemented in the Python codebase.

---

## 1. Data Collection & Telemetry (`collector.py`)
**Purpose:** To poll kernel vitals non-invasively and calculate aging metrics.
*   **Implementation:**
    *   **Memory Parsing:** Opens `/proc/meminfo` and uses string matching (`startswith`) to extract `MemFree`, `SUnreclaim` (Unreclaimable Slab), and `SReclaimable` (Reclaimable Slab).
    *   **Fragmentation Logic:** Parses `/proc/buddyinfo` to count free pages across all orders (0-10). It calculates the **Fragmentation Index ($F$)** using the formula: $F = (Total\ Free - Largest\ Block) / Total\ Free$.
    *   **Scheduling Stats:** Reads `/proc/stat` to capture the `ctxt` (Context Switches) counter.
    *   **Daemon Mode:** Uses a `while True` loop with `time.sleep()` to sample data at a configurable rate.

## 2. CSV Logging System (`logger.py`)
**Purpose:** To provide a persistent, append-only record of system health.
*   **Implementation:**
    *   **Initialization:** Uses the `csv.DictWriter` class to ensure headers are created only if the file doesn't exist.
    *   **Atomic Logging:** Opens the file in `'a'` (append) mode for every entry, ensuring that data is saved even if the system crashes shortly after.
    *   **Field Mapping:** Automatically attaches an ISO-formatted `Timestamp` to every data packet received from the Collector.

## 3. Aging Stressors (`stresser.py`, `realistic_aging.py`)
**Purpose:** To simulate software aging by inducing resource exhaustion.
*   **Implementation (`stresser.py`):**
    *   **Virtual Memory Stress:** Uses `stress-ng --vm` to create rapid allocation/deallocation cycles.
    *   **Slab Bloat:** Uses `stress-ng --dentry` and `--inode-flags` to fill kernel slab caches.
*   **Implementation (`realistic_aging.py`):**
    *   **File System Workload:** Employs `sysbench fileio` to create/delete 1000s of files, simulating a busy file server.
    *   **Persistent Leak:** Uses `ctypes.create_string_buffer` to allocate memory that is *never freed* during the simulation, fragmenting the Buddy System.
    *   **Cleanup Logic:** Uses `glob` and `os.remove` to ensure no `test_file.*` artifacts remain after a run.

## 4. Detection Engine (`engine.py`)
**Purpose:** To determine if the current system state qualifies as "Aged."
*   **Implementation:**
    *   **Benchmarking:** Runs a tight random-access loop over a large list to measure memory access latency.
    *   **Baseline Protocol:** Stores the first successful benchmark as the "Fresh" state baseline.
    *   **Aged State Logic:** Checks if `Frag_Index > 0.75` AND `Current_Latency > (Baseline * 1.1)`. If both are true, it flags the state as "Aged."

## 5. Machine Learning Predictor (`analyzer.py`)
**Purpose:** To estimate "Time-to-Failure" (TTF) based on growth trends.
*   **Implementation:**
    *   **Data Loading:** Reads the CSV log and converts ISO timestamps into Unix epochs for numerical analysis.
    *   **Linear Regression:** Uses `numpy.polyfit(x, y, 1)` to find the slope ($m$) and intercept ($c$) of fragmentation growth over time.
    *   **Prediction:** Solves for $x$ where $Frag\_Index = 0.90$ (Critical Threshold) and returns the remaining time in hours.

## 6. Visualization Engine (`visualizer.py`)
**Purpose:** To generate graphical reports of system health trends.
*   **Implementation:**
    *   **Headless Plotting:** Uses `matplotlib.use('Agg')` to ensure plots can be generated on servers without a GUI/Display.
    *   **Line Charts:** Plots `Frag_Index` vs. `Time` to show the "aging curve."
    *   **Bar Charts:** Compares Reclaimable vs. Unreclaimable Slab memory for the latest sample.
    *   **Scatter Plots:** Shows the correlation between Fragmentation and Benchmark Latency.

## 7. Software Rejuvenation Engine (`rejuvenator.py`)
**Purpose:** To mitigate aging effects without a system reboot.
*   **Implementation:**
    *   **Strategy A:** Writes levels `1`, `2`, or `3` to `/proc/sys/vm/drop_caches` to free pagecache and slab objects.
    *   **Strategy B:** Writes `1` to `/proc/sys/vm/compact_memory` to trigger the kernel’s internal defragmentation algorithm.
    *   **Audit Phase:** Runs a post-rejuvenation benchmark to calculate the "Rejuvenation Gain" (performance recovery delta).

## 8. Unified CLI (`main.py`)
**Purpose:** To provide a single interface for all framework operations.
*   **Implementation:**
    *   Uses `argparse` with `subparsers` to handle commands like `start`, `stop`, `predict`, `plot`, and `rejuvenate`.
    *   **Auto-Fix Mode:** If started with `--auto-fix`, it links the Collector, Engine, and Rejuvenator into a closed-loop system that fixes the kernel automatically when aging is detected.
