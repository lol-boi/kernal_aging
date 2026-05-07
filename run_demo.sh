#!/bin/bash

# --- Linux Kernel Software Aging Framework: AUTOMATED DEMO ---
# Password provided: guts


# 1. Cleanup old data
echo "[1/6] Cleaning up old logs and artifacts..."
rm -f aging_log.csv fragmentation_plot.png slab_health_plot.png correlation_plot.png
sleep 2

# 2. Start the Data Collection Daemon
echo "[2/6] Starting Telemetry Collector (Terminal 1)..."
python3 main.py start --rate 2 &
COLL_PID=$!
sleep 5 # Allow time to establish baseline

# 3. Induce Realistic Aging
echo "[3/6] Starting Aging Simulator (Inducing stress)..."
echo "      (Simulating File I/O, Scheduler Bloat, and Memory Leaks)"
python3 realistic_aging.py
sleep 2

# 4. Show Predictive Analysis
echo "[4/6] Running Machine Learning Predictor..."
python3 main.py predict
sleep 3

# 5. Perform Rejuvenation
echo "[5/6] Triggering Software Rejuvenation (The Fix)..."
echo "      (Root privileges required for rejuvenation)"
sudo python3 main.py rejuvenate
sleep 5 # Let kernel settle

# 6. Finalize and Visualize
echo "[6/6] Stopping Collector and generating Health Reports..."
kill $COLL_PID
python3 main.py plot

