import psutil
import os
import time
import csv

class OverheadMonitor:
    def __init__(self, output_file="overhead_audit.csv"):
        self.process = psutil.Process(os.getpid())
        self.output_file = output_file
        self.headers = ["Timestamp", "CPU_Percent", "RAM_MB"]
        self._init_log()

    def _init_log(self):
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()

    def audit_once(self):
        """Captures current process resource usage."""
        # interval=0.1 to get a non-zero CPU value
        cpu = self.process.cpu_percent(interval=0.1)
        ram = self.process.memory_info().rss / (1024 * 1024) # MB
        
        from datetime import datetime
        data = {
            "Timestamp": datetime.now().isoformat(),
            "CPU_Percent": cpu,
            "RAM_MB": round(ram, 2)
        }
        
        with open(self.output_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(data)
        return data

    def run_audit(self, duration_sec=60, interval=5):
        print(f"Auditing framework overhead for {duration_sec}s...")
        start_time = time.time()
        while time.time() - start_time < duration_sec:
            usage = self.audit_once()
            print(f"Overhead: {usage['CPU_Percent']}% CPU, {usage['RAM_MB']} MB RAM")
            time.sleep(interval)
        print(f"Audit complete. Results saved to {self.output_file}")

if __name__ == "__main__":
    monitor = OverheadMonitor()
    monitor.run_audit()
