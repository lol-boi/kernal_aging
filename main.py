import argparse
import sys
from collector import Collector
from engine import DetectionEngine
from stresser import Stresser
from analyzer import AgingAnalyzer
from visualizer import AgingVisualizer
from rejuvenator import Rejuvenator
import csv
import os

def start_collector(args):
    collector = Collector(sampling_rate=args.rate)
    collector.auto_fix = args.auto_fix
    collector.start()

def predict_aging(args):
    analyzer = AgingAnalyzer()
    print(analyzer.predict_ttf())

def plot_aging(args):
    visualizer = AgingVisualizer()
    visualizer.generate_plots()

def rejuvenate_system(args):
    rejuvenator = Rejuvenator()
    rejuvenator.run_rejuvenation()

def show_status(args):
    if not os.path.exists("aging_log.csv"):
        print("No log file found.")
        return
    with open("aging_log.csv", 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        print("Log file is empty.")
        return
    latest = rows[-1]
    
    # Calculate Health Score
    engine = DetectionEngine()
    
    # Bug 3 Fix: Find real baseline and latest non-zero latency
    baseline = None
    last_latency = 0.0
    for row in rows:
        lat = float(row.get('Benchmark_Latency', 0.0))
        if lat > 0:
            if baseline is None:
                baseline = lat
            last_latency = lat
            
    engine.baseline_latency = baseline if baseline else 0.5
    current_lat = float(latest.get('Benchmark_Latency', 0.0))
    if current_lat == 0:
        current_lat = last_latency
    
    score = engine.calculate_health_score(
        float(latest['Frag_Index_Order_0']),
        current_lat,
        float(latest['Slab_Unreclaimable'])
    )
    
    print(f"--- System Status ---")
    print(f"Timestamp: {latest['Timestamp']}")
    print(f"Kernel Health Score: {score}/100")
    print(f"MemFree: {latest['MemFree']} kB")
    print(f"Slab_Unreclaimable: {latest['Slab_Unreclaimable']} kB")
    print(f"Frag Index: {latest['Frag_Index_Order_0']}")
    if current_lat > 0:
        print(f"Latest Latency: {current_lat:.4f}s (Baseline: {engine.baseline_latency:.4f}s)")

def generate_report(args):
    if not os.path.exists("aging_log.csv"):
        print("No logs available to generate report.")
        return
    
    from logger import Logger
    logger = Logger()
    if args.json:
        logger.export_to_json("aging_report.json")
    else:
        with open("aging_log.csv", 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            print("Log file is empty.")
            return
        print(f"--- Aging Trend Report ---")
        print(f"Total entries: {len(rows)}")
        print(f"First recorded: {rows[0]['Timestamp']}")
        print(f"Last recorded: {rows[-1]['Timestamp']}")
        print(f"Latest Frag Index: {rows[-1]['Frag_Index_Order_0']}")

def run_overhead_audit(args):
    from overhead_monitor import OverheadMonitor
    monitor = OverheadMonitor()
    monitor.run_audit(duration_sec=args.duration)

def run_benchmark_cmd(args):
    engine = DetectionEngine()
    engine.run_benchmark()

def run_stresser(args):
    stresser = Stresser()
    stresser.run_stress_cycle(scenario=args.scenario)

def run_experiments(args):
    from experiment_manager import ExperimentManager
    manager = ExperimentManager()
    manager.run_comparison_suite()

def run_real_simulation(args):
    from realistic_aging import RealAgingSimulator
    sim = RealAgingSimulator()
    sim.run_full_validation()

def main():
    parser = argparse.ArgumentParser(description="Linux Kernel Software Aging Framework")
    subparsers = parser.add_subparsers(help="Commands")

    # --simulate
    parser_sim = subparsers.add_parser("simulate", help="Run real-world aging scenarios (Microservices, File Server, Leak)")
    parser_sim.set_defaults(func=run_real_simulation)

    # --start
    parser_start = subparsers.add_parser("start", help="Launch the collection daemon")
    parser_start.add_argument("--rate", type=int, default=5, help="Sampling rate in seconds")
    parser_start.add_argument("--auto-fix", action="store_true", help="Enables automatic rejuvenation")
    parser_start.set_defaults(func=start_collector)

    # --status
    parser_status = subparsers.add_parser("status", help="Show current fragmentation and slab health")
    parser_status.set_defaults(func=show_status)

    # --report
    parser_report = subparsers.add_parser("report", help="Generate summary of aging trend")
    parser_report.add_argument("--json", action="store_true", help="Export report as JSON")
    parser_report.set_defaults(func=generate_report)

    # --overhead
    parser_overhead = subparsers.add_parser("overhead", help="Audit the framework's own CPU/RAM usage")
    parser_overhead.add_argument("--duration", type=int, default=60, help="Duration of audit in seconds")
    parser_overhead.set_defaults(func=run_overhead_audit)

    # --experiment
    parser_exp = subparsers.add_parser("experiment", help="Run automated validation experiments (ALT, Baseline vs Managed)")
    parser_exp.set_defaults(func=run_experiments)

    # --benchmark
    parser_bench = subparsers.add_parser("benchmark", help="Run performance test")
    parser_bench.set_defaults(func=run_benchmark_cmd)

    # --predict
    parser_predict = subparsers.add_parser("predict", help="Runs the analyzer to show projected aging trends")
    parser_predict.set_defaults(func=predict_aging)

    # --plot
    parser_plot = subparsers.add_parser("plot", help="Generates and saves health charts as .png files")
    parser_plot.set_defaults(func=plot_aging)

    # --rejuvenate
    parser_rejuvenate = subparsers.add_parser("rejuvenate", help="Manually triggers the rejuvenation module")
    parser_rejuvenate.set_defaults(func=rejuvenate_system)

    # stress (extra command)
    parser_stress = subparsers.add_parser("stress", help="Run memory stresser")
    parser_stress.add_argument("--scenario", choices=["default", "database", "process"], default="default", help="Stress scenario to run")
    parser_stress.set_defaults(func=run_stresser)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
