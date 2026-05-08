import csv
import time
import os
import config
import random

class DetectionEngine:
    def __init__(self, log_file="aging_log.csv"):
        self.log_file = log_file
        self.baseline_latency = None
        self.frag_threshold = config.FRAG_THRESHOLD
        self.latency_multiplier = config.LATENCY_MULTIPLIER

    def run_benchmark(self, iterations=None):
        """
        Refined memory performance benchmark (Tier 2).
        Allocates ~500 random-sized buffers across the heap and accesses them 
        randomly to increase sensitivity to memory fragmentation.
        """
        if iterations is None:
            iterations = config.BENCHMARK_ITERATIONS
        print("Running diagnostic memory benchmark (Refined)...")
        
        # 1. Allocate 500 buffers of random sizes (4KB to 64KB)
        num_buffers = 500
        buffers = []
        for _ in range(num_buffers):
            size = random.randint(4096, 65536)
            buffers.append(bytearray(os.urandom(size)))
        
        # 2. Randomly access them
        start_time = time.time()
        for _ in range(iterations):
            b_idx = random.randint(0, num_buffers - 1)
            buf = buffers[b_idx]
            o_idx = random.randint(0, len(buf) - 1)
            _ = buf[o_idx]
            
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
        frag_penalty = frag_index * 40
        
        # 2. Performance Penalty (up to 30 points)
        perf_penalty = 0
        if self.baseline_latency and latency > 0:
            ratio = latency / self.baseline_latency
            if ratio > 1:
                # Use multiplier from config
                perf_penalty = min(30, (ratio - 1) * (30 / (self.latency_multiplier - 1)))
        
        # 3. Slab Bloat Penalty (up to 30 points)
        slab_penalty = min(30, (slab_unreclaimable / config.SLAB_PENALTY_CEILING_KB) * 30)
        
        score = 100 - (frag_penalty + perf_penalty + slab_penalty)
        return max(0, round(score, 2))

    def send_alert(self, message):
        """Sends an alert via HTTP POST if a webhook is configured."""
        if config.ALERT_WEBHOOK_URL:
            import urllib.request
            import json
            try:
                data = json.dumps({"alert": message, "timestamp": time.time()}).encode('utf-8')
                req = urllib.request.Request(config.ALERT_WEBHOOK_URL, data=data, 
                                            headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    pass
                print(f"Alert sent to {config.ALERT_WEBHOOK_URL}")
            except Exception as e:
                print(f"Failed to send alert: {e}")

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
            msg = "!!! ALERT: KERNEL SOFTWARE AGING DETECTED !!!"
            print(msg)
            self.send_alert(msg)
        
        return is_aged

if __name__ == "__main__":
    engine = DetectionEngine()
    engine.set_baseline()
    engine.analyze_logs()
