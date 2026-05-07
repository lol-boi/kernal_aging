import csv
import os
import numpy as np
from datetime import datetime
import config

class AgingAnalyzer:
    def __init__(self, log_file="aging_log.csv"):
        self.log_file = log_file

    def load_data(self):
        if not os.path.exists(self.log_file):
            return None
        
        data = {h.lower(): [] for h in config.REQUIRED_CSV_HEADERS}
        # Add special key for timestamps
        data["timestamps_raw"] = []
        
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Convert timestamp to seconds from start
                    ts = datetime.fromisoformat(row["Timestamp"]).timestamp()
                    data["timestamps_raw"].append(ts)
                    
                    for h in config.REQUIRED_CSV_HEADERS:
                        key = h.lower()
                        if h == "Timestamp":
                            continue
                        # Uniform handling of missing columns
                        val = row.get(h, 0.0)
                        data[key].append(float(val) if val else 0.0)
                except (ValueError, KeyError):
                    continue
        
        # Mapping back to the expected keys in visualizer
        return {
            "timestamps": data["timestamps_raw"],
            "frag_index": data["frag_index_order_0"],
            "slab_unreclaimable": data["slab_unreclaimable"],
            "slab_reclaimable": data["slab_reclaimable"],
            "latency": data["benchmark_latency"]
        }

    def predict_ttf(self, threshold=None):
        """Predicts Time-to-Failure based on a rolling window of Frag_Index trend."""
        if threshold is None:
            threshold = config.CRITICAL_FRAG_THRESHOLD

        raw_data = self.load_data()
        if not raw_data or len(raw_data["timestamps"]) < 2:
            return "Insufficient data for prediction."

        # Use rolling window for more accurate near-term projection
        window = config.PREDICTION_WINDOW_SAMPLES
        x = np.array(raw_data["timestamps"][-window:])
        y = np.array(raw_data["frag_index"][-window:])
        
        if len(x) < 2:
            return "Insufficient data in rolling window for prediction."

        # Normalize x to start from 0
        start_time = x[0]
        x_norm = x - start_time
        
        # Linear Regression: y = mx + c
        m, c = np.polyfit(x_norm, y, 1)
        
        if m <= 0:
            return f"Frag Index is stable or decreasing in the last {len(x)} samples. No imminent failure predicted."
        
        # threshold = m * t_ttf + c  => t_ttf = (threshold - c) / m
        t_ttf_norm = (threshold - c) / m
        
        # Time remaining from now
        current_time_norm = x[-1] - start_time
        time_remaining = t_ttf_norm - current_time_norm
        
        if time_remaining <= 0:
            return "System has already reached or exceeded the aging threshold."
        
        hours = time_remaining / 3600
        return f"Based on last {len(x)} samples, system will reach critical state (Frag={threshold}) in approximately {hours:.2f} hours."

    def analyze_slab_trend(self):
        """Identify the rate of change in unreclaimable slabs to distinguish between normal load spikes and actual software aging."""
        raw_data = self.load_data()
        if not raw_data or len(raw_data["timestamps"]) < 2:
            return "Insufficient data for slab trend analysis."

        x = np.array(raw_data["timestamps"])
        y = np.array(raw_data["slab_unreclaimable"])

        # Calculate rate of change over a recent window
        window = config.PREDICTION_WINDOW_SAMPLES
        recent_timestamps = x[-window:]
        recent_unreclaimable = y[-window:]

        m, c = np.polyfit(recent_timestamps, recent_unreclaimable, 1)
        
        if m > config.SLAB_GROWTH_THRESHOLD_KB_S:
            return f"Spike detected: Unreclaimable slabs are growing very fast ({m:.2f} kB/s). This may be a load spike."
        elif m > 0:
            return f"Aging detected: Steady growth in unreclaimable slabs ({m:.2f} kB/s)."
        else:
            return f"Normal: Unreclaimable slabs are stable or decreasing ({m:.2f} kB/s)."

if __name__ == "__main__":
    analyzer = AgingAnalyzer()
    print(analyzer.predict_ttf())
