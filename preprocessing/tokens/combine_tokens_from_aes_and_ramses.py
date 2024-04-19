aes_file_name = "tokens.txt"
ramses_file_name = "ramses_tokens.txt"

aes_tokens = []
ramses_tokens = []
tokens = []

duplicate_tokens = 0

aes_file = open(aes_file_name, "r")
ramses_file = open(ramses_file_name, "r")
target_file = open("combined_tokens.txt", "w")

MDC_REPLACEMENTS = [
    ("Ḏ", "D"), ("ḏ", "D"), ("Ꜣ", "A"), ("ꜣ", "A"), ("Ḥ", "H"), 
    ("ꜥ", "a"), ("ḥ", "H"), ("Ḫ","x"), ("ḫ","x"), ("Š","S"), 
    ("š","S"), ("Ṯ","T"), ("ṯ","T"), ("ṱ", "T"), ("ẖ","X"), 
    ("i̯","i"), ("i̯","i"), ("ı͗", "i"), ("ʾ","a"), ("i̯͗","i"), 
    ("i̯","i"), ("j","y"), ("z", "s")
  ]

def to_mdc(line):
    mdc_line = line
    for replacement in MDC_REPLACEMENTS:
        mdc_line = mdc_line.replace(replacement[0], replacement[1])
    return mdc_line


aes_lines = aes_file.readlines()
for line in aes_lines:
    mdc_token = to_mdc(line)
    mdc_token = mdc_token.replace("≡", "=").replace(",", ".")

    if mdc_token not in aes_tokens:
        aes_tokens.append(mdc_token)
        tokens.append(mdc_token)

ramses_lines = ramses_file.readlines()
for line in ramses_lines:
    if line not in ramses_tokens:
        ramses_tokens.append(line)
        if line not in tokens:
            tokens.append(line)
        else:
            duplicate_tokens += 1

for token in tokens:
    target_file.write(token)

print('AES tokens: ', len(aes_tokens))
print('Ramses tokens: ', len(ramses_tokens))
print('Duplicate tokens: ', duplicate_tokens)

aes_file.close()
ramses_file.close()
target_file.close()