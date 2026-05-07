import subprocess
import time
import os
import ctypes

class RealAgingSimulator:
    def __init__(self):
        self.leaked_memory = []

    def start_slow_leak(self, total_mb=500, duration_sec=300):
        """Gradually leaks memory over time and leaves it in RAM."""
        print(f"Starting slow memory leak ({total_mb} MB over {duration_sec}s)...")
        chunk_size = 1024 * 1024  # 1MB
        for _ in range(total_mb):
            self.leaked_memory.append(ctypes.create_string_buffer(chunk_size))
            time.sleep(duration_sec / total_mb)

    def file_system_stress(self, total_size_gb=6, duration_sec=600):
        """Simulates a Busy File Server using sysbench."""
        print(f"Simulating Busy File Server workload ({total_size_gb}GB) for {duration_sec}s...")
        # Prepare large file set to exceed 4GB RAM
        subprocess.run(["sysbench", "fileio", "--file-num=64", f"--file-total-size={total_size_gb}G", "prepare"], 
                       stdout=subprocess.DEVNULL)
        # Run random R/W
        subprocess.run(["sysbench", "fileio", "--file-num=64", f"--file-total-size={total_size_gb}G", 
                        "--file-test-mode=rndrw", f"--time={duration_sec}", "run"],
                       stdout=subprocess.DEVNULL)
        # Cleanup
        subprocess.run(["sysbench", "fileio", "--file-num=64", "cleanup"], stdout=subprocess.DEVNULL)

    def web_microservice_churn(self, duration_sec=600):
        """Simulates high container/process churn by rapidly spawning/killing short-lived workers."""
        print(f"Simulating Web Microservice Churn for {duration_sec}s...")
        start_time = time.time()
        while time.time() - start_time < duration_sec:
            # Spawn many short-lived processes (using 'ls' or 'echo' is fast and creates PID/Slab entries)
            processes = []
            for _ in range(20):
                p = subprocess.Popen(["ls", "-R", "/usr/lib"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                processes.append(p)
            
            time.sleep(1) # Let them run briefly
            for p in processes:
                p.terminate() # Kill them to cause slab cleanup/churn
            time.sleep(0.5)

    def run_full_validation(self):
        """Sequential run of all real-world scenarios."""
        print("=== STARTING REAL-WORLD VALIDATION SUITE (Target: 4GB RAM) ===")
        # 1. Slab Stress (Churn)
        self.web_microservice_churn(duration_sec=300)
        # 2. Memory/Frag Stress (File Server)
        self.file_system_stress(total_size_gb=6, duration_sec=600)
        # 3. Persistent Aging (Leak)
        self.start_slow_leak(total_mb=800, duration_sec=300)
        print("=== VALIDATION SUITE COMPLETE ===")

if __name__ == "__main__":
    simulator = RealAgingSimulator()
    simulator.run_full_validation()
