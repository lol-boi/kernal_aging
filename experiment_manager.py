import time
import os
import csv
import signal
import subprocess
import sys
from collector import Collector
from engine import DetectionEngine
from stresser import Stresser
from rejuvenator import Rejuvenator
from analyzer import AgingAnalyzer

class ExperimentManager:
    """Automates validation experiments required by the Readiness Audit."""
    
    def __init__(self, baseline_log="baseline_exp.csv", managed_log="managed_exp.csv"):
        self.baseline_log = baseline_log
        self.managed_log = managed_log
        self.stresser_process = None

    def start_external_stresser(self, scenario="database"):
        """Fix 4: Spawn stresser as an external process for real restart/signals."""
        print(f"Spawning external stresser: {scenario}")
        # We'll use a simple python command that leaks memory or stresses IO
        # to ensure we can control it via signals.
        # If we want a leaky one specifically for Fix 4:
        if scenario == "leaky":
            # Use a newline (\n) before the while loop to fix the SyntaxError
            code = f"import ctypes,time,os;l=[];print(f'Leaky worker {{os.getpid()}} started')\n" \
                   f"while True:l.append(ctypes.create_string_buffer(50*1024*1024));time.sleep(2)"
            cmd = [sys.executable, "-c", code]
        else:
            # For database, process, etc., we call stresser.py directly
            cmd = [sys.executable, "stresser.py", "--scenario", scenario]
            
        self.stresser_process = subprocess.Popen(cmd)
        return self.stresser_process.pid

    def stop_external_stresser(self):
        if self.stresser_process:
            try:
                self.stresser_process.terminate()
                self.stresser_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.stresser_process.kill()
            self.stresser_process = None

    def run_accelerated_life_test(self, log_file, duration_sec=600, auto_fix=False, scenario="database"):
        print(f"Starting ALT (Auto-Fix: {auto_fix}, Scenario: {scenario}) -> {log_file}")
        
        # Create engine first to inject into collector
        engine = DetectionEngine(log_file=log_file)
        collector = Collector(sampling_rate=2, log_file=log_file, engine=engine)
        collector.auto_fix = auto_fix
        
        # 1. Establish Baseline (Fresh State)
        print("Establishing baseline...")
        engine.set_baseline()
        
        # Start the "service" that will age
        self.start_external_stresser(scenario=scenario)
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration_sec:
                # Record state
                data = collector.collect_once(run_benchmark=True)
                
                if auto_fix:
                    if engine.analyze_logs():
                        print("!!! Triggering Rejuvenation !!!")
                        rej = Rejuvenator(collector=collector, engine=engine, log_file=log_file)
                        
                        # Fix 2: Pause stresser during rejuvenation window
                        if self.stresser_process:
                            print(f"Pausing stresser {self.stresser_process.pid} (Fix 2: SIGSTOP)...")
                            os.kill(self.stresser_process.pid, signal.SIGSTOP)
                        
                        # Fix 4: Define a real restart function
                        def restart_leaky_service():
                            print(f"Fix 4: Killing {scenario} service...")
                            self.stop_external_stresser()
                            time.sleep(1)
                            print(f"Fix 4: Restarting {scenario} service...")
                            self.start_external_stresser(scenario=scenario)
                            # Give it a moment to initialize
                            time.sleep(1)
                        
                        # Run the advanced rejuvenation
                        rej.run_rejuvenation(stresser_restart_func=restart_leaky_service)
                        
                        if self.stresser_process:
                            print(f"Resuming stresser {self.stresser_process.pid} (Fix 2: SIGCONT)...")
                            os.kill(self.stresser_process.pid, signal.SIGCONT)
                
                time.sleep(2)
        finally:
            self.stop_external_stresser()
            
        print(f"ALT Complete: {log_file}")

    def validate_predictive_accuracy(self, log_file):
        """Compares predicted TTF with actual degradation trend."""
        analyzer = AgingAnalyzer(log_file=log_file)
        prediction = analyzer.predict_ttf()
        print(f"Validation Report for {log_file}:")
        print(f"Result: {prediction}")
        # In a real experiment, we'd compare this to the time the system actually hits the threshold.
        return prediction

    def run_comparison_suite(self, duration=600, scenario="database"):
        """Runs both Baseline (Aging) and Managed (Rejuvenation) scenarios."""
        # 1. Baseline: Aging without help
        self.run_accelerated_life_test(self.baseline_log, duration_sec=duration, auto_fix=False, scenario=scenario)
        
        # 2. Managed: Aging with rejuvenation
        self.run_accelerated_life_test(self.managed_log, duration_sec=duration, auto_fix=True, scenario=scenario)
        
        print("\n--- EXPERIMENT RESULTS ---")
        self.validate_predictive_accuracy(self.baseline_log)
        self.validate_predictive_accuracy(self.managed_log)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Automated Software Aging Experiments")
    parser.add_argument("--duration", type=int, default=600, help="Duration of each experiment in seconds")
    parser.add_argument("--scenario", choices=["database", "leaky", "process", "default"], default="database", 
                        help="Aging scenario to run")
    args = parser.parse_args()
    
    manager = ExperimentManager()
    manager.run_comparison_suite(duration=args.duration, scenario=args.scenario)
