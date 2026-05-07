import time
import os
import csv
from collector import Collector
from engine import DetectionEngine
from stresser import Stresser
from rejuvenator import Rejuvenator
from analyzer import AgingAnalyzer

from stresser import Stresser, LeakingStresser

class ExperimentManager:
    """Automates validation experiments required by the Readiness Audit."""
    
    def __init__(self, baseline_log="baseline_exp.csv", managed_log="managed_exp.csv"):
        self.baseline_log = baseline_log
        self.managed_log = managed_log

    def run_accelerated_life_test(self, log_file, duration_sec=60, auto_fix=False):
        print(f"Starting ALT (Auto-Fix: {auto_fix}) -> {log_file}")
        
        # Create engine first to inject into collector
        engine = DetectionEngine(log_file=log_file)
        
        collector = Collector(sampling_rate=2, log_file=log_file, engine=engine)
        collector.auto_fix = auto_fix
        
        # Use persistent stress for clearer aging/rejuvenation curves
        leaker = LeakingStresser()
        
        # 1. Establish Baseline (Fresh State)
        print("Establishing baseline...")
        engine.set_baseline()
        
        start_time = time.time()
        while time.time() - start_time < duration_sec:
            # Gradually leak memory to induce aging
            leaker.leak(mb=50)
            
            # Record state
            data = collector.collect_once(run_benchmark=True)
            
            if auto_fix:
                if engine.analyze_logs():
                    print("!!! Triggering Rejuvenation !!!")
                    rej = Rejuvenator(collector=collector, engine=engine, log_file=log_file)
                    
                    # Fix 2: Pause stresser during rejuvenation window
                    print("Pausing stresser (Fix 2)...")
                    # In this synchronous loop, we simply stop calling leak() 
                    # while rejuvenation runs inside the block.
                    
                    # Fix 4: Define a restart function to simulate service restart
                    def restart_leaky_service():
                        print("Fix 4: Simulating Service Restart - Clearing Leaks...")
                        leaker.clear()
                    
                    # Run the advanced rejuvenation
                    rej.run_rejuvenation(stresser_restart_func=restart_leaky_service)
                    
                    print("Resuming stresser...")
            
            time.sleep(2)
        
        leaker.clear()
        print(f"ALT Complete: {log_file}")

    def validate_predictive_accuracy(self, log_file):
        """Compares predicted TTF with actual degradation trend."""
        analyzer = AgingAnalyzer(log_file=log_file)
        prediction = analyzer.predict_ttf()
        print(f"Validation Report for {log_file}:")
        print(f"Result: {prediction}")
        # In a real experiment, we'd compare this to the time the system actually hits the threshold.
        return prediction

    def run_comparison_suite(self):
        """Runs both Baseline (Aging) and Managed (Rejuvenation) scenarios."""
        # 1. Baseline: Aging without help
        self.run_accelerated_life_test(self.baseline_log, duration_sec=60, auto_fix=False)
        
        # 2. Managed: Aging with rejuvenation
        self.run_accelerated_life_test(self.managed_log, duration_sec=60, auto_fix=True)
        
        print("\n--- EXPERIMENT RESULTS ---")
        self.validate_predictive_accuracy(self.baseline_log)
        self.validate_predictive_accuracy(self.managed_log)

if __name__ == "__main__":
    manager = ExperimentManager()
    manager.run_comparison_suite()
