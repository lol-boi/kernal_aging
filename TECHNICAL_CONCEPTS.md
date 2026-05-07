# Technical Concepts: Linux Kernel Software Aging Framework

To fully master this project and answer questions from a technical panel, you should be familiar with the following concepts across four key domains:

---

## 1. Operating Systems & Linux Kernel
*   **Software Aging:** The phenomenon where long-running software experience performance degradation or failure due to resource exhaustion (e.g., memory leaks, fragmentation, unreleased handles).
*   **The Buddy System:** The primary algorithm used by the Linux kernel to manage physical memory. It splits and merges blocks of memory in powers of two to reduce fragmentation.
*   **External Fragmentation:** A state where total free memory is high, but it is split into many small, non-contiguous blocks, making it impossible to satisfy large allocation requests.
*   **Slab Allocator:** A kernel-level memory management mechanism that caches small, frequently used objects (like inodes, dentries, and process descriptors) to avoid expensive allocation cycles.
*   **Virtual Filesystem (`/proc`):** A pseudo-filesystem in Linux that acts as an interface to internal kernel data structures. It allows userspace tools to "read" kernel state (like memory and CPU stats) as if they were regular files.

## 2. Memory Management
*   **Pagecache:** The kernel’s primary disk cache. It stores data recently read from or written to the disk in RAM to improve performance. Clearing it (rejuvenation) can free up significant memory.
*   **Memory Compaction:** A kernel-level defragmentation process that moves allocated pages to one side of the memory to create larger, contiguous free blocks for the Buddy System.
*   **Dentries & Inodes:** Metadata structures that represent directories and files. High file system activity can "bloat" these caches in the Slab allocator.

## 3. Machine Learning & Predictive Analytics
*   **Time-to-Failure (TTF):** A metric used to predict the remaining operational time of a system before it hits a critical failure or unacceptable performance degradation.
*   **Linear Regression:** A foundational statistical method used to model the relationship between a dependent variable (e.g., Fragmentation) and an independent variable (e.g., Time). It calculates a "line of best fit" ($y = mx + c$).
*   **Baseline Protocol:** The process of establishing a "healthy" state against which future performance is measured to detect anomalies or degradation.
*   **Metric Correlation:** The statistical relationship between two variables—in this project, how increasing memory fragmentation correlates with increasing benchmark latency.

## 4. Software Reliability & Engineering
*   **Software Rejuvenation:** A proactive "counter-aging" technique that involves cleaning up internal system state to prevent future failures, often avoiding a full system reboot.
*   **Closed-Loop Control:** A system that automatically senses its state (Collector), analyzes it (Engine), and takes corrective action (Rejuvenator) without human intervention.
*   **Headless Visualization:** The process of generating graphical reports (plots) on a server without a physical monitor or graphical user interface (GUI), typically using backend libraries like Matplotlib’s `Agg`.
*   **Synthetic Workloading:** Using tools like `stress-ng` and `sysbench` to simulate months of real-world server stress in a short, controlled period.
