import time
import os
import subprocess
from collector import Collector
from visualizer import AgingVisualizer
from realistic_aging import RealAgingSimulator
import threading

def run_scenario(name, log_file, duration, sim_func, *args):
    print(f"\n>>> RUNNING SCENARIO: {name} ({duration}s) <<<")
    
    # Clean old log if exists
    if os.path.exists(log_file):
        os.remove(log_file)
        
    # Start collector in a background thread
    collector = Collector(sampling_rate=5, log_file=log_file)
    # We want benchmark to show performance drop
    stop_event = threading.Event()
    
    def collect_loop():
        while not stop_event.is_set():
            collector.collect_once(run_benchmark=True)
            time.sleep(collector.sampling_rate)
            
    thread = threading.Thread(target=collect_loop)
    thread.start()
    
    try:
        # Run the simulation
        sim_func(*args, duration_sec=duration)
    finally:
        # Stop collector
        stop_event.set()
        thread.join()
        
    print(f">>> Scenario {name} complete. Generating plots...")
    
    # Generate plots for this specific scenario
    viz = AgingVisualizer(log_file=log_file)
    viz.generate_plots()
    
    # Rename plots to avoid overwriting
    os.rename("fragmentation_plot.png", f"{name}_frag.png")
    os.rename("slab_health_plot.png", f"{name}_slab.png")
    os.rename("correlation_plot.png", f"{name}_corr.png")
    print(f">>> Plots saved as {name}_*.png")

def main():
    sim = RealAgingSimulator()
    
    # Scenario 1: Web Microservice (Slab Churn)
    run_scenario("web", "web_showcase.csv", 120, sim.web_microservice_churn)
    
    # Scenario 2: File Server (Memory/Pagecache Stress)
    # Using 5GB to exceed 4GB RAM
    run_scenario("db", "db_showcase.csv", 120, sim.file_system_stress, 5)
    
    # Scenario 3: Memory Leak (Persistent Fragmentation)
    run_scenario("leak", "leak_showcase.csv", 120, sim.start_slow_leak, 400)

    print("\n=== ALL SHOWCASE DATA GENERATED ===")

if __name__ == "__main__":
    main()
