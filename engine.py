import csv
import time
import os

class DetectionEngine:
    def __init__(self, log_file="aging_log.csv"):
        self.log_file = log_file
        self.baseline_latency = None
        self.frag_threshold = 0.75
        self.latency_multiplier = 1.1

    def run_benchmark(self, iterations=1000000):
        """Standard memory performance benchmark."""
        print("Running memory benchmark...")
        start_time = time.time()
        # Create a large list and perform random access
        data = [i for i in range(100000)]
        for _ in range(iterations):
            _ = data[(_ * 7) % 100000]
        end_time = time.time()
        latency = end_time - start_time
        print(f"Benchmark Latency: {latency:.4f}s")
        return latency

    def set_baseline(self):
        """Establishes baseline latency on a 'fresh' state."""
        self.baseline_latency = self.run_benchmark()
        print(f"Baseline established: {self.baseline_latency:.4f}s")
        return self.baseline_latency

    def calculate_health_score(self, frag_index, latency, slab_unreclaimable):
        """
        Calculates a consolidated Kernel Health Score (0-100).
        100 = Perfect Health, < 50 = Critical Aging.
        """
        # 1. Fragmentation Penalty (up to 40 points)
        # 0.0 frag = 0 penalty, 1.0 frag = 40 penalty
        frag_penalty = frag_index * 40
        
        # 2. Performance Penalty (up to 30 points)
        perf_penalty = 0
        if self.baseline_latency and latency > 0:
            ratio = latency / self.baseline_latency
            if ratio > 1:
                # 1.5x latency = 30 point penalty
                perf_penalty = min(30, (ratio - 1) * 60)
        
        # 3. Slab Bloat Penalty (up to 30 points)
        # Assume > 500MB unreclaimable is bad for small systems
        slab_penalty = min(30, (slab_unreclaimable / 512000) * 30)
        
        score = 100 - (frag_penalty + perf_penalty + slab_penalty)
        return max(0, round(score, 2))

    def analyze_logs(self):
        """Checks if current state is 'Aged'."""
        if not os.path.exists(self.log_file):
            print("No logs found for analysis.")
            return

        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            print("Logs are empty.")
            return

        latest = rows[-1]
        frag_index = float(latest["Frag_Index_Order_0"])
        latest_latency = float(latest["Benchmark_Latency"])
        # Use latest benchmark if logged, otherwise run one
        current_latency = latest_latency if latest_latency > 0 else self.run_benchmark()

        is_aged = False
        if frag_index > self.frag_threshold:
            if self.baseline_latency and current_latency > (self.baseline_latency * self.latency_multiplier):
                is_aged = True
        
        status = "Aged State Detected" if is_aged else "Normal"
        baseline_str = f"{self.baseline_latency:.4f}s" if self.baseline_latency is not None else "N/A"
        print(f"--- Analysis Report ---")
        print(f"Frag Index: {frag_index}")
        print(f"Latency: {current_latency:.4f}s (Baseline: {baseline_str})")
        print(f"Status: {status}")
        
        if is_aged:
            print("!!! ALERT: KERNEL SOFTWARE AGING DETECTED !!!")
        
        return is_aged

if __name__ == "__main__":
    engine = DetectionEngine()
    engine.set_baseline()
    engine.analyze_logs()
