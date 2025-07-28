#!/bin/bash
# Usage: ./plot_profile.sh profile_prefix

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <profile_prefix> (e.g. ./plot_profile.sh report1)"
    exit 1
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PREFIX="$1"
SQLITE_FILE="${PREFIX}.sqlite"
CSV_FILE="${PREFIX}_timeline.csv"
STATS_PREFIX="${PREFIX}_kernel_stats"
STATS_FILE="${STATS_PREFIX}_gpukernsum.csv"
TOP_KERNELS_FILE="${PREFIX}_top_kernels.txt"
TIMELINE_PNG_FILE="${PREFIX}_timeline.png"
SUMMARY_PNG_FILE="${PREFIX}_summary.png"

# Extract start, end, kernel_name (join with StringIds)
sqlite3 -header -csv "$SQLITE_FILE" "
  SELECT k.start, k.end, s.value AS kernel_name
  FROM CUPTI_ACTIVITY_KIND_KERNEL k
  JOIN StringIds s ON k.demangledName = s.id
  ORDER BY k.start;
" > "$CSV_FILE"

# Get kernel statistics from nsys stats
echo "Running nsys stats on $SQLITE_FILE..."
nsys stats --format csv -o "$STATS_PREFIX" "$SQLITE_FILE"
if [ ! -f "$STATS_FILE" ]; then
  STATS_FILE="${STATS_PREFIX}_cuda_gpu_kern_sum.csv"
fi

# Extact kernels with > 2% kernel time
python3 ${SCRIPT_DIR}/scripts/extract_top_kernels.py "$STATS_FILE" "$TOP_KERNELS_FILE"

# Plot Timeline and Boxplot
echo "Plotting..."
python3 ${SCRIPT_DIR}/scripts/plot_kernels.py "$CSV_FILE" "$STATS_FILE" "$TOP_KERNELS_FILE" "$TIMELINE_PNG_FILE"
python3 ${SCRIPT_DIR}/scripts/plot_kernels_summary.py "$CSV_FILE" "$TOP_KERNELS_FILE" "$SUMMARY_PNG_FILE"

echo "Done. Output saved to: $TIMELINE_PNG_FILE and $SUMMARY_PNG_FILE"
