import os
import time
from collector import Collector
from engine import DetectionEngine

class Rejuvenator:
    def __init__(self, collector=None, engine=None, log_file="aging_log.csv"):
        self.log_file = log_file
        # Dependency Injection
        from collector import Collector
        from engine import DetectionEngine
        self.collector = collector if collector else Collector(log_file=log_file)
        self.engine = engine if engine else DetectionEngine(log_file=log_file)

    def _is_root(self):
        return os.getuid() == 0

    def drop_caches(self, level=3):
        """1: pagecache, 2: dentries/inodes, 3: all."""
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

    def force_slab_reclaim(self, size_mb=500):
        """Fix 1: Induce slab shrinkage via transient memory pressure."""
        print(f"Inducing Slab Reclaim via {size_mb}MB pressure...")
        try:
            # Allocate a large buffer to force kernel to reclaim slab
            import ctypes
            pressure_buffer = ctypes.create_string_buffer(size_mb * 1024 * 1024)
            time.sleep(1) # Hold briefly
            del pressure_buffer # Free it
            return True
        except Exception as e:
            print(f"Slab reclaim pressure failed: {e}")
            return False

    def compact_memory(self):
        """Trigger a single pass of memory compaction."""
        if not self._is_root(): return False
        try:
            with open("/proc/sys/vm/compact_memory", "w") as f:
                f.write("1")
            return True
        except:
            return False

    def adaptive_compaction(self, threshold=0.005, max_passes=10):
        """Fix 5: Loop compaction until frag index stops improving."""
        print("Starting Adaptive Compaction...")
        last_frag = 1.0
        for i in range(max_passes):
            self.compact_memory()
            time.sleep(0.5)
            # Sample current frag
            current_frag = self.collector.get_buddyinfo()["Frag_Index_Order_0"]
            delta = last_frag - current_frag
            print(f"Pass {i+1}: Frag Index = {current_frag:.4f} (Delta: {delta:.4f})")
            if delta < threshold and i > 0:
                print("Compaction stabilized.")
                break
            last_frag = current_frag
        return True

    def restart_service(self, target_process_name=None):
        """Fix 4: Service restart to reclaim SUnreclaim."""
        if target_process_name:
            print(f"Fix 4: Restarting service {target_process_name} to reclaim SUnreclaim...")
            # For this experiment, we handle the restart logic in experiment_manager.py
            # but we define the strategy here.
            return True
        return False

    def run_rejuvenation(self, stresser_restart_func=None):
        # 1. Capture "Before" state
        print("Starting Advanced Rejuvenation Audit...")
        before = self.collector.collect_once(run_benchmark=True)
        before_bench = before["Benchmark_Latency"]

        # 2. Rejuvenate
        if self.drop_caches(3):
            # Fix 1: Pressure reclaim
            self.force_slab_reclaim(500)
            
            # Fix 5: Adaptive compaction (First pass)
            self.adaptive_compaction()

            # Fix 4: Restart leaky service if provided
            if stresser_restart_func:
                stresser_restart_func()

            # Fix 3: Increase settling time to 10s
            print("Waiting 10s for kernel to settle (Fix 3)...")
            time.sleep(10)

            # Fix 3: Second compaction pass after settling
            print("Second compaction pass...")
            self.compact_memory()
            time.sleep(1)

            # 3. Capture "After" state
            after = self.collector.collect_once(run_benchmark=True)
            after_bench = after["Benchmark_Latency"]
            
            # 4. Report Gain
            frag_gain = before["Frag_Index_Order_0"] - after["Frag_Index_Order_0"]
            slab_gain = before["Slab_Unreclaimable"] - after["Slab_Unreclaimable"]
            perf_gain = before_bench - after_bench
            
            print(f"--- Advanced Rejuvenation Report ---")
            print(f"Fragmentation Delta: {frag_gain:.4f}")
            print(f"Slab Unreclaim Delta: {slab_gain:.4f} kB")
            print(f"Performance Delta: {perf_gain:.4f}s")
            return True
        return False

if __name__ == "__main__":
    rejuvenator = Rejuvenator()
    rejuvenator.run_rejuvenation()
