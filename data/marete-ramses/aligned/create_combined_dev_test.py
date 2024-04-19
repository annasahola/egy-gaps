types = ["dev", "test", "train", "val"]

for t in types:
    if t == "test":
        aes_file = open("../../../preprocessing/final_files/intact/test/harmonized/all_" + t + ".txt", "r")
    else:
        aes_file = open("../../../preprocessing/final_files/intact/dev/harmonized/all_" + t + ".txt", "r")
    ramses_file = open("aligned_transliterations_intact_" + t + ".txt", "r")
    target_file = open("combined_" + t + ".txt", "w")

    al = aes_file.readlines()
    rl = ramses_file.readlines()

    for l in al:
        target_file.write(l)
    
    for l in rl:
        target_file.write(l)

    aes_file.close()
    ramses_file.close()
    target_file.close()