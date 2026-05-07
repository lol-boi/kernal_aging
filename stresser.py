import time
import random
import ctypes
import subprocess
import shutil

class Stresser:
    def __init__(self):
        self.allocated_chunks = []
        self.has_stress_ng = shutil.which("stress-ng") is not None

    def fragment_memory(self, total_mb=300, chunk_size_kb=4):
        """
        If stress-ng is available, use it to fragment memory.
        Otherwise, fallback to custom Python fragmentation.
        """
        if self.has_stress_ng:
            print(f"Using stress-ng to fragment memory ({total_mb} MB)...")
            # --vm 1: One VM worker
            # --vm-bytes: amount of memory
            # --vm-keep: keep redirtying memory to prevent it being swapped/ignored
            # --vm-hang 0: don't sleep between cycles
            # We run it in the background for a short burst to induce fragmentation
            cmd = [
                "stress-ng", "--vm", "2", "--vm-bytes", f"{total_mb // 2}M", 
                "--vm-keep", "--timeout", "10s", "--metrics-brief"
            ]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"stress-ng failed: {e}")
        else:
            print(f"stress-ng not found. Falling back to Python fragmentation ({total_mb} MB)...")
            num_chunks = (total_mb * 1024) // chunk_size_kb
            for _ in range(num_chunks):
                self.allocated_chunks.append(ctypes.create_string_buffer(chunk_size_kb * 1024))
            
            new_list = []
            for i, chunk in enumerate(self.allocated_chunks):
                if i % 2 == 0:
                    new_list.append(chunk)
            self.allocated_chunks = new_list

    def exhaust_slab(self, timeout="10s"):
        """
        Use stress-ng to create many kernel objects (dentries, inodes, etc.)
        to fill up the slab cache.
        """
        if self.has_stress_ng:
            print(f"Using stress-ng to exhaust slab caches for {timeout}...")
            # --dentry: stress directory entries
            # --inode-flags: exercises various inode flags (more compatible)
            cmd = [
                "stress-ng", "--dentry", "1", "--inode-flags", "1", 
                "--timeout", timeout, "--metrics-brief"
            ]
            try:
                # This might require root for some slab objects, but dentry/inode 
                # usually work well for userspace triggers.
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Slab stress failed: {e}")
        else:
            print("Slab exhaustion requires stress-ng (not found).")

    def database_io_stress(self, timeout="10s"):
        """Simulate Database I/O stress."""
        if self.has_stress_ng:
            print(f"Running Database I/O stress scenario for {timeout}...")
            cmd = [
                "stress-ng", "--hdd", "2", "--hdd-bytes", "1G",
                "--io", "2", "--timeout", timeout, "--metrics-brief"
            ]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"DB I/O stress failed: {e}")
        else:
            print("Database I/O stress requires stress-ng (not found).")

    def high_process_creation_stress(self, timeout="10s"):
        """Simulate High-Process creation stress."""
        if self.has_stress_ng:
            print(f"Running High-Process creation stress scenario for {timeout}...")
            cmd = [
                "stress-ng", "--fork", "4", "--exec", "2", "--clone", "2",
                "--timeout", timeout, "--metrics-brief"
            ]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Process creation stress failed: {e}")
        else:
            print("Process creation stress requires stress-ng (not found).")

    def run_stress_cycle(self, scenario="default"):
        try:
            while True:
                if scenario == "database":
                    self.database_io_stress(timeout="10s")
                    time.sleep(2)
                elif scenario == "process":
                    self.high_process_creation_stress(timeout="10s")
                    time.sleep(2)
                else:
                    self.fragment_memory(total_mb=400)
                    time.sleep(2)
                    self.exhaust_slab(timeout="5s")
                    time.sleep(2)
        except KeyboardInterrupt:
            print("Stopping stresser...")

class LeakingStresser:
    """Stresser that keeps memory allocated until cleared to simulate persistent aging."""
    def __init__(self):
        self.leaked = []

    def leak(self, mb=100):
        print(f"Leaking {mb}MB of memory...")
        # Allocate in 1MB chunks to ensure fragmentation
        for _ in range(mb):
            self.leaked.append(ctypes.create_string_buffer(1024 * 1024))

    def clear(self):
        print("Clearing leaked memory...")
        self.leaked.clear()

if __name__ == "__main__":
    stresser = Stresser()
    stresser.run_stress_cycle()
