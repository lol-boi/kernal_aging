import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from analyzer import AgingAnalyzer

class AgingVisualizer:
    def __init__(self, log_file="aging_log.csv"):
        self.analyzer = AgingAnalyzer(log_file)

    def generate_plots(self):
        data = self.analyzer.load_data()
        if not data or not data["timestamps"]:
            print("No data available to plot.")
            return

        # Normalize timestamps to start from 0 (seconds from start)
        start_time = data["timestamps"][0]
        norm_timestamps = [ts - start_time for ts in data["timestamps"]]

        # 1. Fragmentation vs. Time
        plt.figure(figsize=(10, 5))
        plt.plot(norm_timestamps, data["frag_index"], label="Frag Index", color='red')
        plt.title("Fragmentation vs. Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Frag Index")
        plt.legend()
        plt.savefig("fragmentation_plot.png")
        print("Saved fragmentation_plot.png")

        # 2. Slab Health (latest point)
        plt.figure(figsize=(10, 5))
        labels = ['Unreclaimable', 'Reclaimable']
        values = [data["slab_unreclaimable"][-1], data["slab_reclaimable"][-1]]
        plt.bar(labels, values, color=['gray', 'green'])
        plt.title("Latest Slab Health")
        plt.ylabel("Size (kB)")
        plt.savefig("slab_health_plot.png")
        print("Saved slab_health_plot.png")

        # 3. Correlation (Scatter)
        # Only plot where latency > 0
        valid_indices = [i for i, l in enumerate(data["latency"]) if l > 0]
        if valid_indices:
            frag_subset = [data["frag_index"][i] for i in valid_indices]
            lat_subset = [data["latency"][i] for i in valid_indices]
            plt.figure(figsize=(10, 5))
            plt.scatter(frag_subset, lat_subset, color='blue')
            plt.title("Frag Index vs. Benchmark Latency")
            plt.xlabel("Frag Index")
            plt.ylabel("Latency (s)")
            plt.savefig("correlation_plot.png")
            print("Saved correlation_plot.png")
        else:
            print("No latency data available for correlation plot.")

if __name__ == "__main__":
    visualizer = AgingVisualizer()
    visualizer.generate_plots()
