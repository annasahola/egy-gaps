import sklearn.model_selection

file_name = "aligned_transliterations_intact.txt"
file = open(file_name, "r")
file_lines = file.readlines()

file_dev, file_test = sklearn.model_selection.train_test_split(file_lines, test_size=0.20, train_size=0.80, random_state=42)
file_train, file_val = sklearn.model_selection.train_test_split(file_dev, test_size=0.25, train_size=0.75, random_state=42)

dev_file = open("aligned_transliterations_intact_dev.txt", "w")
train_file = open("aligned_transliterations_intact_train.txt", "w")
test_file = open("aligned_transliterations_intact_test.txt", "w")
val_file = open("aligned_transliterations_intact_val.txt", "w")

for line in file_dev:
    dev_file.write(line)

for line in file_train:
    train_file.write(line)

for line in file_test:
    test_file.write(line)

for line in file_val:
    val_file.write(line)

file.close()
dev_file.close()
train_file.close()
test_file.close()
val_file.close()
