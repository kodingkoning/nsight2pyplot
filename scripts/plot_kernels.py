import sys
import csv
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.cm import ScalarMappable
from mpl_toolkits.axes_grid1 import make_axes_locatable

if len(sys.argv) != 5:
    print("Usage: plot_kernels.py kernel_timeline.csv summary_csv_file.csv top_kernels.txt output.png")
    sys.exit(1)

csv_file = sys.argv[1]
summary_csv_file = sys.argv[2]
top_kernels_file = sys.argv[3]
output_file = sys.argv[4]

# Load top kernels set
with open(top_kernels_file) as f:
    top_kernels = set(line.strip() for line in f if line.strip())

# Store kernel execution intervals by kernel name
kernel_groups = defaultdict(list)
with open(csv_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["kernel_name"].strip()
        if name not in top_kernels:
            name = "other"
        start = int(row["start"]) / 1e6
        duration = (int(row["end"]) / 1e6) - start
        kernel_groups[name].append((start, duration))

# Find kernel percentages
kernel_percent = {}
with open(summary_csv_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["Name"].strip()
        if name in top_kernels:
            try:
                kernel_percent[name] = f"{row['Time(%)'].strip()}% "
            except KeyError:
                kernel_percent[name] = f"{row['Time (%)'].strip()}% "

# Sort kernel names putting 'other' last
kernel_names = sorted(kernel_groups.keys(), key=lambda k: (k == "other", k))

# Reverse order: top kernel at top (largest y), other at bottom (y=0)
kernel_names.reverse()

# Create list of kernel percentages to use for labels
kernel_percent_list = []
for kern in kernel_names:
    if kern == "other":
        kernel_percent_list.append("")
    else:
        kernel_percent_list.append(kernel_percent[kern])


# Truncate labels > 25 chars with ellipsis
def truncate_label(label, max_len=25):
    if len(label) > max_len:
        return label[:max_len-3] + "..."
    return label

truncated_labels = [truncate_label(name) for name in kernel_names]

# Calculate values for plot positioning
y_locs = {name: i for i, name in enumerate(kernel_names)}

fig_height = max(3, len(kernel_names) * 0.25)
fig, ax = plt.subplots(figsize=(15, fig_height))

colors = plt.cm.tab20.colors
short_threshold = 3e3

bar_colors = []
edge_colors = []
y_values = []
bar_values = []

# Save durations of kernels
for i, name in enumerate(kernel_names):
    y = y_locs[name]
    color = colors[i % len(colors)]
    long_bars = []
    short_bars = []
    edgecolors = []
    for start, duration in kernel_groups[name]:
        long_bars.append((start, duration))
        edgecolors.append('gray')
    edge_colors.append(edgecolors)
    y_values.append(y)
    bar_values.append(long_bars)

# Calculate the gradient of the colored bars
min_dur = bar_values[0][0][1]
max_dur = bar_values[0][0][1]
for values in bar_values:
    durations = [x[1] for x in values]
    if max(durations) > max_dur:
        max_dur = max(durations)
    if min(durations) < min_dur:
        min_dur = min(durations)

# Create color map
norm = mcolors.Normalize(vmin=min_dur, vmax=max_dur)
cmap = cm.get_cmap('RdYlGn_r')  # green=short, red=long

# Create legend
sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])  # Dummy array for compatibility
for values in bar_values:
    colors = []
    for bar in values:
        colors.append(cmap(norm(bar[1])))
    bar_colors.append(colors)

# Add the durations to the chart
for i in range(len(bar_values)):
    ax.broken_barh(bar_values[i], (y_values[i] - 0.4, 0.8), facecolors=bar_colors[i], linewidth=0.05, edgecolor=bar_colors[i], linestyle='solid')

ax.set_yticks(list(y_locs.values()))
ax.set_yticklabels(truncated_labels)
ax.set_xlabel("Time (ms)")
ax.set_title("CUDA Kernel Execution Timeline (>2% labeled)")
ax.grid(True, axis='x', linestyle='--', alpha=0.3)

# Create twin y-axis on the right
ax_right = ax.twinx()
ax_right.set_ylim(ax.get_ylim())  # match the limits
ax_right.set_yticks(list(y_locs.values()))
ax_right.set_yticklabels(kernel_percent_list)

# Turn off right tick marks
ax_right.tick_params(axis='y', which='both', length=0)

cbar = plt.colorbar(sm, ax=ax_right)
cbar.set_label('Kernel Duration (ms)')  # Label for the legend

plt.tight_layout()

# Auto-size left margin to fit y-axis labels
fig.canvas.draw()
labels = ax.get_yticklabels()
renderer = fig.canvas.get_renderer()
max_width = max(label.get_window_extent(renderer).width for label in labels)

fig_width_px = fig.get_figwidth() * fig.dpi
margin_left = max_width / fig_width_px + 0.02  # padding
if margin_left > 0.8:
    margin_left = 0.8

plt.subplots_adjust(left=margin_left,right=1.05)

plt.savefig(output_file, dpi=500)
