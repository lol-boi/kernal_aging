import csv
import os
from datetime import datetime

class Logger:
    def __init__(self, filename="aging_log.csv"):
        self.filename = filename
        self.headers = [
            "Timestamp", 
            "MemFree", 
            "Slab_Unreclaimable", 
            "Slab_Reclaimable",
            "Slab_Active_Objs",
            "Slab_Total_Objs",
            "Frag_Index_Order_0", 
            "Frag_Index_Order_10", 
            "Context_Switches",
            "Benchmark_Latency"
        ]
        self._initialize_csv()

    def _initialize_csv(self):
        """Creates the CSV file with headers if it doesn't already exist."""
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()

    def export_to_json(self, output_file="aging_report.json"):
        """Exports the CSV log to a JSON file."""
        import json
        if not os.path.exists(self.filename):
            print(f"Log file {self.filename} not found.")
            return
        
        data = []
        with open(self.filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Exported logs to {output_file}")

    def log(self, data):
        """
        Appends a row to the CSV log.
        Ensures only keys matching self.headers are logged.
        :param data: Dictionary containing telemetry data.
        """
        data["Timestamp"] = datetime.now().isoformat()
        
        # Create a filtered dict with only valid headers, filling missing with 0.0
        row = {}
        for h in self.headers:
            row[h] = data.get(h, 0.0)
            
        with open(self.filename, mode='a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(row)

if __name__ == "__main__":
    # Quick test
    logger = Logger("test_log.csv")
    test_data = {
        "MemFree": 1024,
        "Slab_Unreclaimable": 256,
        "Frag_Index_Order_0": 0.5,
        "Frag_Index_Order_10": 0.2,
        "Benchmark_Latency": 1.5
    }
    logger.log(test_data)
    print(f"Logged test data to {logger.filename}")
