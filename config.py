import os

# --- Thresholds & Logic ---
FRAG_THRESHOLD = 0.60
LATENCY_MULTIPLIER = 1.02
CRITICAL_FRAG_THRESHOLD = 0.90

# --- Slab Analysis ---
SLAB_PENALTY_CEILING_KB = 512000
SLAB_GROWTH_THRESHOLD_KB_S = 500

# --- Prediction Window ---
PREDICTION_WINDOW_SAMPLES = 20

# --- Alerting ---
ALERT_WEBHOOK_URL = os.getenv("AGING_ALERT_WEBHOOK", None) # e.g., "http://localhost:8080/alert"

# --- Stress Limits ---
MAX_LEAK_CEILING_MB = 1500

# --- Benchmark Settings ---
BENCHMARK_ITERATIONS = 1000000
REQUIRED_CSV_HEADERS = [
    "Timestamp", 
    "MemFree", 
    "Slab_Unreclaimable", 
    "Slab_Reclaimable",
    "Slab_Active_Objs",
    "Slab_Total_Objs",
    "Frag_Index_Order_0", 
    "Frag_Index_Order_10", 
    "Context_Switches",
    "Benchmark_Latency"
]
