import csv
import os
import numpy as np
from datetime import datetime

class AgingAnalyzer:
    def __init__(self, log_file="aging_log.csv"):
        self.log_file = log_file

    def load_data(self):
        if not os.path.exists(self.log_file):
            return None
        
        data = {
            "timestamps": [],
            "frag_index": [],
            "slab_unreclaimable": [],
            "slab_reclaimable": [],
            "latency": []
        }
        
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Convert timestamp to seconds from start
                    ts = datetime.fromisoformat(row["Timestamp"]).timestamp()
                    data["timestamps"].append(ts)
                    data["frag_index"].append(float(row["Frag_Index_Order_0"]))
                    data["slab_unreclaimable"].append(float(row["Slab_Unreclaimable"]))
                    data["slab_reclaimable"].append(float(row.get("Slab_Reclaimable", 0)))
                    data["latency"].append(float(row["Benchmark_Latency"]))
                except (ValueError, KeyError):
                    continue
        return data

    def predict_ttf(self, threshold=0.9):
        """Predicts Time-to-Failure based on Frag_Index trend."""
        raw_data = self.load_data()
        if not raw_data or len(raw_data["timestamps"]) < 2:
            return "Insufficient data for prediction."

        x = np.array(raw_data["timestamps"])
        y = np.array(raw_data["frag_index"])
        
        # Normalize x to start from 0
        start_time = x[0]
        x_norm = x - start_time
        
        # Linear Regression: y = mx + c
        m, c = np.polyfit(x_norm, y, 1)
        
        if m <= 0:
            return "Frag Index is stable or decreasing. No imminent failure predicted."
        
        # threshold = m * t_ttf + c  => t_ttf = (threshold - c) / m
        t_ttf_norm = (threshold - c) / m
        
        # Time remaining from now
        current_time_norm = x_norm[-1]
        time_remaining = t_ttf_norm - current_time_norm
        
        if time_remaining <= 0:
            return "System has already reached or exceeded the aging threshold."
        
        hours = time_remaining / 3600
        return f"Based on fragmentation growth, system will reach critical state (Frag={threshold}) in approximately {hours:.2f} hours."

    def analyze_slab_trend(self):
        """Identify the rate of change in unreclaimable slabs to distinguish between normal load spikes and actual software aging."""
        raw_data = self.load_data()
        if not raw_data or len(raw_data["timestamps"]) < 2:
            return "Insufficient data for slab trend analysis."

        x = np.array(raw_data["timestamps"])
        y = np.array(raw_data["slab_unreclaimable"])

        # Calculate rate of change over a recent window (e.g., last 10 samples)
        window = min(10, len(x))
        recent_timestamps = x[-window:]
        recent_unreclaimable = y[-window:]

        m, c = np.polyfit(recent_timestamps, recent_unreclaimable, 1)
        
        # Rate of change is m (kB/s).
        # We can define a threshold to distinguish spike vs steady growth.
        # A steady, positive slope indicates aging. A very high transient slope or negative slope implies spikes or normal operation.
        
        if m > 500: # Example threshold
            return f"Spike detected: Unreclaimable slabs are growing very fast ({m:.2f} kB/s). This may be a load spike."
        elif m > 0:
            return f"Aging detected: Steady growth in unreclaimable slabs ({m:.2f} kB/s)."
        else:
            return f"Normal: Unreclaimable slabs are stable or decreasing ({m:.2f} kB/s)."

if __name__ == "__main__":
    analyzer = AgingAnalyzer()
    print(analyzer.predict_ttf())
