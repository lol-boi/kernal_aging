import time
import os
from logger import Logger

class Collector:
    def __init__(self, sampling_rate=5, log_file="aging_log.csv", engine=None):
        self.sampling_rate = sampling_rate
        self.logger = Logger(log_file)
        self.auto_fix = False
        self.engine = engine # Inject engine to avoid runtime imports

    def get_meminfo(self):
        """Parse /proc/meminfo for MemFree, SUnreclaim, and SReclaimable."""
        data = {"MemFree": 0, "Slab_Unreclaimable": 0, "Slab_Reclaimable": 0}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemFree:"):
                    data["MemFree"] = int(line.split()[1])
                elif line.startswith("SUnreclaim:"):
                    data["Slab_Unreclaimable"] = int(line.split()[1])
                elif line.startswith("SReclaimable:"):
                    data["Slab_Reclaimable"] = int(line.split()[1])
        return data

    def get_buddyinfo(self):
        """
        Parse /proc/buddyinfo to calculate Frag Index.
        F = (Total Free - Largest Free Block) / Total Free
        """
        # We'll focus on Order 0 and Order 10 as per spec fields
        # Frag_Index_Order_0 and Frag_Index_Order_10 in spec might mean 
        # indices calculated for those specific orders or general frag.
        # Let's calculate a global frag index based on buddyinfo.
        
        total_free_pages = 0
        largest_free_pages = 0
        
        # buddyinfo format: Node X, zone Y <counts for orders 0-10>
        try:
            with open("/proc/buddyinfo", "r") as f:
                for line in f:
                    parts = line.split()
                    counts = [int(x) for x in parts[4:]]
                    for order, count in enumerate(counts):
                        pages = count * (2**order)
                        total_free_pages += pages
                        if pages > largest_free_pages:
                            largest_free_pages = pages
        except FileNotFoundError:
            return {"Frag_Index_Order_0": 0.0, "Frag_Index_Order_10": 0.0}

        if total_free_pages == 0:
            frag_index = 0.0
        else:
            frag_index = (total_free_pages - largest_free_pages) / total_free_pages

        # Simplification: we'll use the same calculated index for both fields for now
        # or adapt if the spec implies something more specific.
        return {
            "Frag_Index_Order_0": round(frag_index, 4),
            "Frag_Index_Order_10": round(frag_index, 4) # Placeholder logic
        }

    def get_context_switches(self):
        """Parse /proc/stat for total context switches."""
        try:
            with open("/proc/stat", "r") as f:
                for line in f:
                    if line.startswith("ctxt"):
                        return int(line.split()[1])
        except (FileNotFoundError, IndexError, ValueError):
            return 0
        return 0

    def get_slabinfo(self):
        """Parse /proc/slabinfo for active objects and total objects."""
        # Note: /proc/slabinfo usually requires root.
        data = {"Slab_Active_Objs": 0, "Slab_Total_Objs": 0}
        try:
            if not os.path.exists("/proc/slabinfo"):
                return data
            with open("/proc/slabinfo", "r") as f:
                lines = f.readlines()
                # Skip header lines
                for line in lines[2:]:
                    parts = line.split()
                    if len(parts) > 2:
                        data["Slab_Active_Objs"] += int(parts[1])
                        data["Slab_Total_Objs"] += int(parts[2])
        except (PermissionError, FileNotFoundError, ValueError):
            pass
        return data

    def collect_once(self, run_benchmark=False):
        mem_data = self.get_meminfo()
        frag_data = self.get_buddyinfo()
        slab_data = self.get_slabinfo()
        ctxt_switches = self.get_context_switches()
        
        latency = 0.0
        if run_benchmark and self.engine:
            # Use injected engine
            latency = self.engine.run_benchmark(iterations=1000000)

        combined_data = {
            **mem_data, 
            **frag_data, 
            **slab_data,
            "Context_Switches": ctxt_switches,
            "Benchmark_Latency": latency
        }
        self.logger.log(combined_data)
        return combined_data

    def start(self, rejuvenator=None):
        print(f"Starting collection every {self.sampling_rate} seconds...")
        
        # Ensure engine is set if auto_fix is enabled
        if self.auto_fix and not self.engine:
            from engine import DetectionEngine
            self.engine = DetectionEngine(log_file=self.logger.filename)
            self.engine.set_baseline()

        if self.auto_fix and not rejuvenator:
            from rejuvenator import Rejuvenator
            rejuvenator = Rejuvenator(collector=self, engine=self.engine, log_file=self.logger.filename)

        sample_count = 0
        try:
            while True:
                sample_count += 1
                # Run benchmark every 3 samples (e.g. every 15s if rate=5)
                should_bench = (sample_count % 3 == 0)
                data = self.collect_once(run_benchmark=should_bench)
                print(f"Collected: {data}")
                
                if self.auto_fix and self.engine and rejuvenator:
                    if self.engine.analyze_logs():
                        print("!!! AUTO-FIX TRIGGERED !!!")
                        rejuvenator.run_rejuvenation()
                        
                time.sleep(self.sampling_rate)
        except KeyboardInterrupt:
            print("Stopping collection...")

if __name__ == "__main__":
    collector = Collector(sampling_rate=2, log_file="collector_test.csv")
    collector.collect_once()
    print("One-shot collection complete. Check collector_test.csv")
