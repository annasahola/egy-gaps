import re

file_name = "alignedLines_ramsesTrainingSet.txt"

i = 1

file = open(file_name, "r")
lines = file.readlines()

target_file = open("aligned_transliterations.txt", "w")

for line in lines:
    if i % 3 == 2:
        cleaned_line = line

        cleaned_line = cleaned_line.replace("_ - _", "_ LACUNA _").replace("_ - _", "_ LACUNA _")

        cleaned_line = cleaned_line.replace(" ", "").replace("_", " ").replace("(", "").replace(")", "").replace("<", "").replace(">", "")


        cleaned_line = cleaned_line.replace("LACUNA", "<LACUNA>").replace("PARTIAL_LACUNA", "<PARTIAL_LACUNA>").replace("[]", "<PARTIAL_LACUNA>").replace("[ ]", "<PARTIAL_LACUNA>").replace("///", "<PARTIAL_LACUNA>")
        
        cleaned_line = cleaned_line.replace("[...]", "<PARTIAL_LACUNA>")

        cleaned_line = re.sub("(^- )", "<LACUNA>", cleaned_line)

        # these cases were all partial lacuna
        cleaned_line = cleaned_line.replace("[?]", "<PARTIAL_LACUNA>")

        cleaned_line = cleaned_line.replace("?", "<LACUNA>")

        # some full lacunas marked with [] --> partial lacuna to full lacuna
        cleaned_line = re.sub("[ \n](<PARTIAL_LACUNA>)[ \n]", " <LACUNA> ", cleaned_line)
        cleaned_line = re.sub("(^<PARTIAL_LACUNA>)[ \n]", " <LACUNA> ", cleaned_line)

        # classifiers?
        cleaned_line = cleaned_line.replace("//", "")
        # replace space fillers
        cleaned_line = cleaned_line.replace("---", "")

        cleaned_line = cleaned_line.replace("[", "").replace("]", "")

        cleaned_line = cleaned_line.replace(" +", " -")

        cleaned_line = cleaned_line.strip()
        target_file.write(cleaned_line + "\n")
    i += 1

file.close()
target_file.close()