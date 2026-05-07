import os
import time
from collector import Collector
from engine import DetectionEngine

class Rejuvenator:
    def __init__(self, log_file="aging_log.csv"):
        self.log_file = log_file
        self.collector = Collector(log_file=log_file)
        self.engine = DetectionEngine(log_file=log_file)

    def _is_root(self):
        return os.getuid() == 0

    def drop_caches(self, level=3):
        """
        1: Free pagecache
        2: Free dentries and inodes
        3: Free pagecache, dentries and inodes
        """
        if not self._is_root():
            print("ERROR: Rejuvenation requires root privileges (sudo).")
            return False
        
        print(f"Executing Strategy A: drop_caches (level {level})...")
        try:
            with open("/proc/sys/vm/drop_caches", "w") as f:
                f.write(str(level))
            return True
        except Exception as e:
            print(f"Failed to drop caches: {e}")
            return False

    def compact_memory(self, times=5):
        """Trigger the kernel's memory compaction algorithm multiple times."""
        if not self._is_root():
            print("ERROR: Rejuvenation requires root privileges (sudo).")
            return False

        print(f"Executing Strategy B: compact_memory ({times} cycles)...")
        try:
            for _ in range(times):
                with open("/proc/sys/vm/compact_memory", "w") as f:
                    f.write("1")
                time.sleep(0.5) # Wait briefly between cycles
            return True
        except Exception as e:
            print(f"Failed to compact memory: {e}")
            return False

    def run_rejuvenation(self):
        # 1. Capture "Before" state
        print("Starting Rejuvenation Audit...")
        before = self.collector.collect_once(run_benchmark=True)
        before_bench = before["Benchmark_Latency"]

        # 2. Rejuvenate
        if self.drop_caches(3) and self.compact_memory(5):
            # Wait for kernel to settle
            time.sleep(5)

            # 3. Capture "After" state
            after = self.collector.collect_once(run_benchmark=True)
            after_bench = after["Benchmark_Latency"]
            
            # 4. Report Gain
            frag_gain = before["Frag_Index_Order_0"] - after["Frag_Index_Order_0"]
            perf_gain = before_bench - after_bench
            
            print(f"--- Rejuvenation Report ---")
            print(f"Fragmentation Delta: {frag_gain:.4f}")
            print(f"Performance Delta: {perf_gain:.4f}s")
            return True
        return False

if __name__ == "__main__":
    rejuvenator = Rejuvenator()
    rejuvenator.run_rejuvenation()
