import csv
import sys

# Crates a text file with the names of kernels above 2% of the total kernel time in the profiling summary in the CSV file

if len(sys.argv) != 3:
    print("Usage: extract_top_kernel.py input_csv output_txt")
    sys.exit(1)

input_csv = sys.argv[1]
output_txt = sys.argv[2]

with open(input_csv, newline='') as csvfile, open(output_txt, 'w') as out:
    reader = csv.DictReader(csvfile)
    for row in reader:
        found_percent = False
        try:
            pct = float(row["Time(%)"])
            found_percent = True
        except (KeyError, ValueError):
            try:
                pct = float(row["Time (%)"])
                found_percent = True
            except (KeyError, ValueError):
                pass
        if found_percent and pct > 2.0:
            out.write(row["Name"] + "\n")
