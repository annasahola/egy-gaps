file_name = "aligned_transliterations.txt"

file = open(file_name, "r")
lines = file.readlines()

target_file = open("aligned_transliterations_tokens.txt", "w")

tokens = []

for line in lines:
    for token in line.split():
        if "<PARTIAL_LACUNA>" not in token and "<LACUNA>" not in token:
            if token not in tokens:
                tokens.append(token)

for token in tokens:
    target_file.write(token + "\n")

file.close()
target_file.close()