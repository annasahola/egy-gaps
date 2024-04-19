import re

file_name = "aligned_transliterations.txt"

file = open(file_name, "r")
lines = file.readlines()

target_file_i = open("aligned_transliterations_intact.txt", "w")
target_file_g = open("aligned_transliterations_gaps.txt", "w")

for line in lines:
    if "<PARTIAL_LACUNA>" in line or "<LACUNA>" in line:
        target_file_g.write(line)
    else:
        target_file_i.write(line)

file.close()
target_file_i.close()
target_file_g.close()