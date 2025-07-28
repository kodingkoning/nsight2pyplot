import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Calculate durations of kernels
def kernel_data(kernel_df, kernel_name):
    this_kernel_df = kernel_df[kernel_df['kernel_name'] == kernel_name]
    return (this_kernel_df['end'] - this_kernel_df['start']) / 1e6

def main(timeline_file, top_kernels_file, output_file):
    # Load data
    df = pd.read_csv(timeline_file)

    # Load top kernels set
    with open(top_kernels_file) as f:
        top_kernels = set(line.strip() for line in f if line.strip())

    # Extract data for boxplots
    boxplot_data = []
    labels = []
    for kernel_name in top_kernels:
        time_data = kernel_data(df, kernel_name)
        boxplot_data.append(time_data)
        labels.append(kernel_name)

    if not boxplot_data:
        print("No matching kernels found.")
        return

    # Reverse data to place first kernel at the top of the plot
    boxplot_data = boxplot_data[::-1]
    labels = labels[::-1]

    # Truncate labels > 25 chars with ellipsis
    def truncate_label(label, max_len=25):
        if len(label) > max_len:
            return label[:max_len-3] + "..."
        return label

    labels = [truncate_label(name) for name in labels]

    # Plot boxplots
    fig, ax = plt.subplots(figsize=(12, 6))
    bp = ax.boxplot(boxplot_data, vert=False, patch_artist=True, labels=labels,
                    boxprops=dict(facecolor='skyblue', color='blue'),
                    medianprops=dict(color='red'),
                    whiskerprops=dict(color='blue'),
                    capprops=dict(color='blue'),
                    flierprops=dict(marker='o', color='gray', alpha=0.5, markersize=3))

    ax.set_xlabel("Kernel Duration (ms)")
    ax.set_title("Top Kernels Boxplot Summary")
    ax.grid(True, axis='x', linestyle='--', alpha=0.6)

    # Auto-size left margin to fit y-axis labels
    fig.canvas.draw()
    labels = ax.get_yticklabels()
    renderer = fig.canvas.get_renderer()
    max_width = max(label.get_window_extent(renderer).width for label in labels)
    fig_width_px = fig.get_figwidth() * fig.dpi
    margin_left = max_width / fig_width_px + 0.02  # padding
    if margin_left > 0.8:
        margin_left = 0.8
    plt.subplots_adjust(left=margin_left)

    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Saved boxplot to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python plot_kernels_summary.py kernel_timeline_stats.csv top_kernels.csv output.png")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
