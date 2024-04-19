import json
import re
import sklearn.model_selection
import argparse

parser = argparse.ArgumentParser(description='Run preprocessing code')
parser.add_argument('--harmonized', default=False, action=argparse.BooleanOptionalAction, help='create files with a harmonized transliteration style')

args = parser.parse_args()
HARMONIZED = args.harmonized

AES_FILENAMES = ["_aes_bbawamarna.json", "_aes_bbawhistbiospzt.json", "_aes_sawmedizin.json", "_aes_bbawarchive.json", "_aes_bbawpyramidentexte.json", "_aes_bbawbriefe.json", "_aes_bbawramessiden.json", "_aes_smaek.json", "_aes_bbawfelsinschriften.json", "_aes_bbawtempelbib.json", "_aes_tb.json", "_aes_bbawgrabinschriften.json", "_aes_bbawtotenlit.json", "_aes_tuebingerstelen.json", "_aes_bbawgraeberspzt.json", "_aes_sawlit.json"]
LACUNAE_TYPES = ["<LACUNAE_UNKNOWN_LENGTH>", "<LACUNAE_WORD>", "<LACUNAE_PARTIAL>", "<VERB>", "<SUBST>", "<PREP>", "<PN>", "<KN>", "<GN>", "<ON>", "<NUM>"]
STRUCTURAL_SIGNS = [":", "=", ".", ",", "!", "-", "~", ";"]
TOKENS = []
SUFFIX_TOKENS = []
SPLIT_TOKENS = []

MDC_REPLACEMENTS = [
    ("Ḏ", "D"), ("ḏ", "D"), ("Ꜣ", "A"), ("ꜣ", "A"), ("Ḥ", "H"), 
    ("ꜥ", "a"), ("ḥ", "H"), ("Ḫ","x"), ("ḫ","x"), ("Š","S"), 
    ("š","S"), ("Ṯ","T"), ("ṯ","T"), ("ṱ", "T"), ("ẖ","X"), 
    ("i̯","i"), ("i̯","i"), ("ı͗", "i"), ("ʾ","a"), ("i̯͗","i"), 
    ("i̯","i"), ("j","y"), ("z", "s")
  ]


def to_mdc(line):
  sent_id = ""
  # check if sentence ID is included
  if ">" in line:
    sent_id = line[:line.index(">") + 1]
    mdc_line = line[line.index(">") + 1:]
  else:
    mdc_line = line
  
  for replacement in MDC_REPLACEMENTS:
    mdc_line = mdc_line.replace(replacement[0], replacement[1])
  return sent_id + mdc_line

def extract_sentences(result_file_ending):
  for aes_file in AES_FILENAMES:
    print("Opening file:", aes_file)
    file = open("../data/aes/" + aes_file, "r")
    data = json.load(file)

    result_file_name = aes_file.split(".")[0] + result_file_ending
    print("Writing sentences into temp_results/" + result_file_name + "...")
    result_file = open("temp_results/" + result_file_name, "w")

    for e in data:
      sentence_object = data[e]
      token_list = sentence_object["token"]
      sentence = []
      for token in token_list:
        written_form = token["written_form"]
        sentence.append(written_form)
    
      result_file.write("<" + e + "> " + " ".join(sentence) + "\n")

    file.close()
    result_file.close()

def clean_line(line):
  sentence = line

  # person names, person titles, place names
  name_replacements = [
    ("-PN-", "<PN>"), ("-(PN)-", "<PN>"), ("-QN-", "<PN>"), ("-(QN)-", "<PN>"), ("PN//m", "<PN>"),
    ("-TI-", "<TI>"), ("-(TI)-", "<TI>"),
    ("-KN-", "<KN>"), ("-(KN)-", "<KN>"),
    ("-ON-", "<ON>"),
    ("-GN-", "<GN>"), ("-Gn-", "<GN>"), ("-[GN]-", "<GN>")
  ]

  for nr in name_replacements:
    sentence = sentence.replace(nr[0], nr[1])

  pos_replacements = [
    ("-Zahl-", "<NUM>"), ("-(Zahl)-", "<NUM>"),
    ("-Jahreszeit-", "<TIME>"), ("-(Jahreszeit)-", "<TIME>"), ("-Jahresseit-", "<TIME>"), ("-(Jahresseit)-", "<TIME>"),
    ("-Präp.-", "<PREP>"), ("-(Präp.)-", "<PREP>"), ("-〈(Präp.)〉-", "<PREP>"),
    ("-Subst.-", "<SUBST>"), ("-(Subst.)-", "<SUBST>"),
    ("-Vb-", "<VERB>"), ("-(Vb)-", "<VERB>"),
    ("-Vb.-", "<VERB>"), ("-(Vb.)-", "<VERB>"),
    ("-Verb-", "<VERB>"), ("-(Verb)-", "<VERB>"), ("-〈(Verb)〉-", "<VERB>")
  ]

  for posr in pos_replacements:
    sentence = sentence.replace(posr[0], posr[1])

  sentence = sentence.replace("[...] -w- [...]", "[...]-w-[...]")
  sentence = sentence.replace("-.-", "")

  sentence = sentence.replace("--", "[___]").replace("⸢??⸣", "[___]")

  w_lacunae = ["-W-", "-(W)-", "-(W-)", "-[W]-", "-WS-"]

  for wl in w_lacunae:
    sentence = sentence.replace(wl, "[___]")
  sentence = sentence.replace("-(w)-w", "[___]w")

  # ancient deletions (keep in, remove curly brackets)
  sentence = sentence.replace("{{", "").replace("}}", "")

  # PLURALS

  sentence = sentence.replace(" =ø", "")

  # get rid of duals (not used in Ramses transliterations)
  sentence = sentence.replace(".(Du.)", "").replace(".du", "")

  # get rid of plurals (not used in Ramses transliterations)
  dot_pls = [".(Pl.)", "(.Pl.)", ".Pl", ".pl", ".[pl]", ".⸢pl⸣", ".⸮pl?", ".[⸮pl?]"]
  for dp in dot_pls:
    sentence = sentence.replace(dp, "")

  comma_pls = [",pl", ",[pl]", ",⸢pl⸣", ",⸮pl?", ",[⸮pl?]"]
  for cp in comma_pls:
    sentence = sentence.replace(cp, "")

  combined_pl_replacemenets = [
    (",jwpl", ",jw"), (",jpl", ",j"), 
    (",tpl", ",t"), (".wpl", ".w"), 
    (".ypl", ".y"), (".tpl", ".t"), 
    (",[t.]pl", "[,t]")
    ]
  
  for cpr in combined_pl_replacemenets:
    sentence = sentence.replace(cpr[0], cpr[1])
  
  sentence = sentence.replace("-pl-", "").replace("-pl", "")

  sentence = sentence.replace("[j.]", "[j]")

  # get rid of random hieroglyph unicode
  sentence = sentence.replace("𓊆", "").replace("𓊇", "")
  sentence = sentence.replace("𓊇", "")

  # name typo?
  sentence = sentence.replace("[-ꜥnḫ]⸢-Špss-kꜣ≡f⸣", "⸢Špss-kꜣ≡f⸣[-ꜥnḫ]")

  # descriptive pictures(?) sometimes denoted with -?- ?
  sentence = sentence.replace("-?-", "<DESCRIPTIVE_PICTURE>").replace("-??-", "<DESCRIPTIVE_PICTURE>").replace("-[??]-", "<DESCRIPTIVE_PICTURE>").replace("-⸮?-", "<DESCRIPTIVE_PICTURE>")
  
  sentence = re.sub("\.\{\S+?\}(\w)", r".\1", sentence)
  sentence = re.sub("\.\{\S+?\}([\〈\(\[\{]+?)\.?", r".\1", sentence)

  # name typo?
  sentence = sentence.replace("Pṯḥ", "Ptḥ")

  # some special cases
  special_case_replacements = [
    ("⸢wr.⸣pl", "⸢wr⸣.pl"), ("[ḫpr,]pl", "[ḫpr],pl"),
    ("[nn]-[ḥr]-ḥ,[pl≡f]", "[nn]-[ḥr]-ḥ[,pl≡f]"), ("[(j)m(,j)-r(ʾ)-mšꜥ,]pl", "[(j)m(,j)-r(ʾ)-mšꜥ],pl"),
    ("jtr,w.[pl-n-pꜣ-tꜣ-n-Ḫt]", "jtr,w[.pl-n-pꜣ-tꜣ-n-Ḫt]"), ("nfr.{t}-ḥr", "nfr-ḥr"),
    ("sḫpr.{⸮n?}.n", "sḫpr{.⸮n?}.n"), ("⸮ḥwt-nTr...?", "ḥwt-nTr[___]"),
    ("jḥ.〈〈.pl〉〉", "jḥ〈〈.pl〉〉"), ("ꜣtp ={w}〈.w〉", "ꜣtp〈.w〉"),
    ("=(..)", "=[__]"), ("⸮ꜣš[..]j?", "ꜣš[__]j")
  ]

  for sr in special_case_replacements:
    sentence = sentence.replace(sr[0], sr[1])

  # erraneous personal suffixes
  sentence = re.sub(" ?={\S+?} ", " ", sentence)
  sentence = re.sub(" ?={\S+?}\n", "\n", sentence)
  sentence = re.sub(" ?=\⸮{\S+?}\? ", " ", sentence)
  sentence = re.sub(" ?=\⸮{\S+?}\?\n", "\n", sentence)
  sentence = re.sub(" ?=\[{\S+?}\] ", " ", sentence)
  sentence = re.sub(" ?=\[{\S+?}\]\n", "\n", sentence)
  sentence = re.sub(" ?=\[{\⸮\S+?\?}\] ", " ", sentence)
  sentence = re.sub(" ?=\[{\⸮\S+?\?}\]\n", "\n", sentence)
  # get rid of possible extra spaces/newlines generated by above
  sentence = re.sub(" {2,}", " ", sentence)
  sentence = re.sub("\n{2,}", " ", sentence)

  # some lacunae marked with ...?..., 〈...〉 etc.
  lacunae_replacements = [("...?...", "[...]"), ("[⸮-?]", "[...]"), ("[?]", "[...]"), ("[.]", "[_]"), ("〈...〉", "[...]"), ("-Lücke--", "[...]")]
  for lr in lacunae_replacements:
    sentence = sentence.replace(lr[0], lr[1])

  # ancient additions (keep in, remove parenthesis)
  sentence = sentence.replace("((", "").replace("))", "")
  # ancient reconstructions (keep in, remove brackets)
  sentence = sentence.replace("[[", "").replace("]]", "")

  # surround non-bracket-marked lacunae with []
  sentence = re.sub(r"(\_+)", r"[\1]", sentence)
  sentence = sentence.replace("[[", "[").replace("]]", "]")

  # remove parenthesis around editor expansions ()
  sentence = sentence.replace("(", "").replace(")", "")
  # remove erraneous and superfluous parts {}
  sentence = re.sub("\{.*?\}", "", sentence)
  # remove signs for erraneous omissions and haplographies
  sentence = sentence.replace("〈", "").replace("〉", "")
  # replace "⸮_?" with []
  sentence = sentence.replace("⸮", "[").replace("?", "]")

  # get rid of exclamation marks (not used in Ramses transliterations)
  sentence = sentence.replace("!!", "").replace("!", "")

  # correct that one instance...
  sentence = sentence.replace("≡=", "≡")

  special_case_replacements_2 = [
    ("I͗...", "I͗[___]"), ("⸢..w⸣", "[__]⸢w⸣"), ("jmj-rʾ-pr-...", "jmj-rʾ-pr-[___]"),
    ("...ḥꜣb", "[___]ḥꜣb"), ("...wjꜣ", "[___]wjꜣ"), ("...rnp,t", "[___]rnp,t"),
    ("///ṯw,t", "[___]ṯw,t"), ("ꜥꜣm//ḥn//", "ꜥꜣm[__]ḥn[__]"), ("-/nḫt", "[__]nḫt")
  ]

  for scr in special_case_replacements_2:
    sentence = sentence.replace(scr[0], scr[1])

  lacunae_replacements_2 = [
    ("//", "[...]"), ("/A24/", "[...]"), ("/ꜣ24/", "[...]"), ("/N5/", "[...]"), ("/Y1/", "[...]"),
    ("1...n", "[_]"),
    ("-1Q-", "[_]"), ("..1Q..", "[_]"), ("..2Q..", "[__]"), ("...Q...", "[...]"), ("...2-3Q...", "[___]"),
    (" ... ", "[...]"), (" .. ", "[__]"),
    ("jpw-...", "jpw-[___]")
  ]

  for lr in lacunae_replacements_2:
    sentence = sentence.replace(lr[0], lr[1])

  sentence = re.sub("\. ", " ", sentence)

  # get rid of plural markers (not used in Ramses transliterations) that were not caught above
  sentence = sentence.replace(".du", "")
  sentence = sentence.replace(".wpl", ".w").replace(".typl", ".ty").replace("tpl", "t").replace("jpl", "j")
  sentence = sentence.replace(".pl", "").replace("-pl-", "").replace("-pl", "").replace(",pl", "").replace("pl", "")

  sentence = sentence.replace("+", "")
  sentence = sentence.replace("--", "-")

  # harmonize equal signs
  sentence = sentence.replace("≡", "=")

  # remove any lone structural signs
  sentence = sentence.replace(" : ", "").replace(" = ", "").replace(" . ", "").replace(" , ", "").replace(" ! ", "").replace(" - ", "").replace(" ~ ", "").replace(" ; ", "")

  return sentence

def clean(origin_file_ending, result_file_ending):
  print("Cleaning sentences...")
  for aes_file in AES_FILENAMES:
    file_name = aes_file.split(".")[0] + origin_file_ending
    print("Opening file:", file_name)
    file = open("temp_results/" + file_name, "r")
    file_lines = file.readlines()

    result_file_name = file_name.split(".")[0] + result_file_ending
    print("Writing sentences into temp_results/" + result_file_name + "...")
    result_file = open("temp_results/" + result_file_name, "w")

    for line in file_lines:
      sentence = clean_line(line)
      if len(sentence.split(">", 1)[1].strip()) > 0:
        result_file.write(sentence)

    file.close()
    result_file.close()

def divide_sentences_to_files(origin_file_ending):
  for aes_file in AES_FILENAMES:
    file_name = aes_file.split(".")[0] + origin_file_ending
    print("Opening file:", file_name)
    file = open("temp_results/" + file_name, "r")
    file_lines = file.readlines()

    gap_result_file_name = file_name.split(".")[0] + "_gaps.txt"
    filled_result_file_name = file_name.split(".")[0] + "_filled.txt"
    fully_intact_result_file_name = file_name.split(".")[0] + "_fully_intact.txt"
    intact_result_file_name = file_name.split(".")[0] + "_intact.txt"
    print("Writing sentences into temp_results/" + gap_result_file_name + "/..._filled.txt/..._fully_instact.txt/..._intact.txt...")
    gap_result_file = open("temp_results/" + gap_result_file_name, "w")
    filled_result_file = open("temp_results/" + filled_result_file_name, "w")
    fully_intact_result_file = open("temp_results/" + fully_intact_result_file_name, "w")
    intact_result_file = open("temp_results/" + intact_result_file_name, "w")

    for line in file_lines:
      # do gaps exist?
      gap_regex = r"\[\.\.\.\]" # gap of unknown length
      gap_specified_length_regex = r"\[\_+\]" # gaps of known length
      if re.search(gap_regex, line) or re.search(gap_specified_length_regex, line):
        gap_result_file.write(line)
      # no gaps (but might have editor guesses)
      else:
        intact_result_file.write(line)
        # check if filled by editor / has damaged parts or fully intact
        bracket_regex = r"\[.*\]"
        small_bracket_regex = r"\⸢.*\⸣"
        if re.search(bracket_regex, line) or re.search(small_bracket_regex, line):
          filled_result_file.write(line)
        else:
          fully_intact_result_file.write(line)

    file.close()
    gap_result_file.close()
    filled_result_file.close()
    fully_intact_result_file.close()
    intact_result_file.close()

def replace_gaps(line):
  sentence = line
  # replace gaps
  # unknown length gap
  sentence = sentence.replace("[...]", "<LACUNAE_UNKNOWN_LENGTH>")
  # known length gap
  sentence = sentence.replace(" [___] ", " <LACUNAE_WORD> ")
  sentence = sentence.replace(" [___]\n", " <LACUNAE_WORD>\n")
  sentence = sentence.replace(" [__] ", " <LACUNAE_WORD> ")
  sentence = sentence.replace(" [__]\n", " <LACUNAE_WORD>\n")
  sentence = sentence.replace(" [_] ", " <LACUNAE_WORD> ")
  sentence = sentence.replace(" [_]\n", " <LACUNAE_WORD>\n")
  # partial gap
  sentence = sentence.replace("[___]", "<LACUNAE_PARTIAL>")
  sentence = sentence.replace("[__]", "<LACUNAE_PARTIAL>")
  sentence = sentence.replace("[_]", "<LACUNAE_PARTIAL>")
  # replace []
  sentence = sentence.replace("[", "").replace("]", "")
  # replace small brackets
  sentence = sentence.replace("⸢", "").replace("⸣", "")

  sentence = sentence.replace("--", "-")

  return sentence

def handle_file(file_name, result_file_name, folder):
  print("Opening files:", file_name)
  file = open("temp_results/" + file_name, "r")
  file_lines = file.readlines()

  print("Writing sentences into temp_results/" + result_file_name)
  result_file = open("final_files/" + folder + "/" + result_file_name, "w")

  for line in file_lines:
    sentence = replace_gaps(line)
    result_file.write(sentence)
  
  file.close()
  result_file.close()

def get_final_files():
  for aes_file in AES_FILENAMES:
    file_name_gaps = aes_file.split(".")[0] + "_sentences_cleaned_gaps.txt"
    file_name_intact = aes_file.split(".")[0] + "_sentences_cleaned_intact.txt"

    gap_result_file_name = aes_file.split(".")[0] + "_gaps.txt"
    intact_result_file_name = aes_file.split(".")[0] + "_intact.txt"

    print("Handling gap file...")
    handle_file(file_name_gaps, gap_result_file_name, "gaps")
    print("Handling intact file...")
    handle_file(file_name_intact, intact_result_file_name, "intact")

def handle_token(token):
  t = token
  if HARMONIZED:
    t = t.replace(",", ".")
    t = to_mdc(t)
  
  if all(lt not in t for lt in LACUNAE_TYPES) and t not in TOKENS:
    TOKENS.append(t)
    
    if any(ss in t for ss in STRUCTURAL_SIGNS):
      # starting_character = t[0]
      structural_sign_reg = r'([\:\=\.\,\!\-\~\;]+[^\:\=\≡\.\,\!\-\~\;]+(?:[\:\=\.\,\!\-\~\;]+$)?)'
      split_tokens = re.split(structural_sign_reg, t)

      for spt in split_tokens:
        if len(spt) > 0 and spt not in SPLIT_TOKENS:
          stripped_spt = spt.rstrip(".,").strip("-")
          SPLIT_TOKENS.append(stripped_spt)

      suffix_tokens = split_tokens[1:]

      for st in suffix_tokens:
        if len(st) > 0 and st not in SUFFIX_TOKENS:
          SUFFIX_TOKENS.append(st)
    else:
      SPLIT_TOKENS.append(t)

def get_unique_tokens():
  for aes_file in AES_FILENAMES:
    gap_file_name = "final_files/gaps/" + aes_file.split(".")[0] + "_gaps.txt"
    print("Opening file:", gap_file_name)
    gap_file = open(gap_file_name, "r")

    gap_file_lines = gap_file.readlines()
    for line in gap_file_lines:
      token_list = line.split()[1:]
      for token in token_list:
        handle_token(token)
    
    gap_file.close()

    intact_file_name = "final_files/intact/" + aes_file.split(".")[0] + "_intact.txt"
    print("Opening file:", intact_file_name)
    intact_file = open(intact_file_name, "r")

    intact_file_lines = intact_file.readlines()
    for line in intact_file_lines:
      token_list = line.split()[1:]
      for token in token_list:
        handle_token(token)

    intact_file.close()

  token_file_name = "tokens/tokens.txt"
  if HARMONIZED:
    token_file_name = "tokens/harmonized/tokens.txt"
  
  print("Writing tokens into file:", token_file_name)
  token_file = open(token_file_name, "w")

  for token in TOKENS:
    token_file.write(token + "\n")

  token_file.close()

  split_token_file_name = "tokens/split_tokens.txt"
  if HARMONIZED:
    split_token_file_name = "tokens/harmonized/split_tokens.txt"
  
  print("Writing split tokens into file:", split_token_file_name)
  split_token_file = open(split_token_file_name, "w")

  for token in SPLIT_TOKENS:
    split_token_file.write(token + "\n")

  split_token_file.close()

  suffix_token_file_name = "tokens/suffix_tokens.txt"
  if HARMONIZED:
    suffix_token_file_name = "tokens/harmonized/suffix_tokens.txt"
  
  print("Writing suffix tokens into file:", suffix_token_file_name)
  suffix_token_file = open(suffix_token_file_name, "w")

  for token in SUFFIX_TOKENS:
    suffix_token_file.write(token + "\n")

  suffix_token_file.close()


def divide_into_sets():
  if HARMONIZED:
    all_result_file = open("final_files/all_intact_harmonized.txt", "w")
    all_dev_result_file = open("final_files/intact/dev/harmonized/all_dev.txt", "w")
    all_train_result_file = open("final_files/intact/dev/harmonized/all_train.txt", "w")
    all_val_result_file = open("final_files/intact/dev/harmonized/all_val.txt", "w")
    all_test_result_file = open("final_files/intact/test/harmonized/all_test.txt", "w")

    all_dev_result_id_file = open("final_files/intact/dev/harmonized/all_dev_id.txt", "w")
    all_train_result_id_file = open("final_files/intact/dev/harmonized/all_train_id.txt", "w")
    all_val_result_id_file = open("final_files/intact/dev/harmonized/all_val_id.txt", "w")
    all_test_result_id_file = open("final_files/intact/test/harmonized/all_test_id.txt", "w")
  else:
    all_result_file = open("final_files/all_intact.txt", "w")
    all_dev_result_file = open("final_files/intact/dev/all_dev.txt", "w")
    all_train_result_file = open("final_files/intact/dev/all_train.txt", "w")
    all_val_result_file = open("final_files/intact/dev/all_val.txt", "w")
    all_test_result_file = open("final_files/intact/test/all_test.txt", "w")

    all_dev_result_id_file = open("final_files/intact/dev/all_dev_id.txt", "w")
    all_train_result_id_file = open("final_files/intact/dev/all_train_id.txt", "w")
    all_val_result_id_file = open("final_files/intact/dev/all_val_id.txt", "w")
    all_test_result_id_file = open("final_files/intact/test/all_test_id.txt", "w")

  for aes_file in AES_FILENAMES:
    file_name = aes_file.split(".")[0] + "_intact.txt"
    # go through each file
    print("Opening file:", file_name)
    file = open("final_files/intact/" + file_name, "r")

    if HARMONIZED:
      dev_result_file = open("final_files/intact/dev/harmonized/" + aes_file.split(".")[0] + "_dev.txt", "w")
      train_result_file = open("final_files/intact/dev/harmonized/" + aes_file.split(".")[0] + "_train.txt", "w")
      val_result_file = open("final_files/intact/dev/harmonized/" + aes_file.split(".")[0] + "_val.txt", "w")
      test_result_file = open("final_files/intact/test/harmonized/" + aes_file.split(".")[0] + "_test.txt", "w")

      dev_result_id_file = open("final_files/intact/dev/harmonized/" + aes_file.split(".")[0] + "_dev_id.txt", "w")
      train_result_id_file = open("final_files/intact/dev/harmonized/" + aes_file.split(".")[0] + "_train_id.txt", "w")
      val_result_id_file = open("final_files/intact/dev/harmonized/" + aes_file.split(".")[0] + "_val_id.txt", "w")
      test_result_id_file = open("final_files/intact/test/harmonized/" + aes_file.split(".")[0] + "_test_id.txt", "w")
    else:
      dev_result_file = open("final_files/intact/dev/" + aes_file.split(".")[0] + "_dev.txt", "w")
      train_result_file = open("final_files/intact/dev/" + aes_file.split(".")[0] + "_train.txt", "w")
      val_result_file = open("final_files/intact/dev/" + aes_file.split(".")[0] + "_val.txt", "w")
      test_result_file = open("final_files/intact/test/" + aes_file.split(".")[0] + "_test.txt", "w")

      dev_result_id_file = open("final_files/intact/dev/" + aes_file.split(".")[0] + "_dev_id.txt", "w")
      train_result_id_file = open("final_files/intact/dev/" + aes_file.split(".")[0] + "_train_id.txt", "w")
      val_result_id_file = open("final_files/intact/dev/" + aes_file.split(".")[0] + "_val_id.txt", "w")
      test_result_id_file = open("final_files/intact/test/" + aes_file.split(".")[0] + "_test_id.txt", "w")

    file_lines = file.readlines()
    
    file_dev, file_test = sklearn.model_selection.train_test_split(file_lines, test_size=0.20, train_size=0.80, random_state=42)
    file_train, file_val = sklearn.model_selection.train_test_split(file_dev, test_size=0.25, train_size=0.75, random_state=42)

    for lt in file_dev:
      line = lt
      if HARMONIZED:
        line = lt.replace(",", ".")
        line = to_mdc(line)
      
      dev_result_file.write(" ".join(line.split()[1:]) + "\n")
      dev_result_id_file.write(line)

      all_dev_result_file.write(" ".join(line.split()[1:]) + "\n")
      all_dev_result_id_file.write(line)

      all_result_file.write(" ".join(line.split()[1:]) + "\n")

    for lt in file_test:
      line = lt
      if HARMONIZED:
        line = lt.replace(",", ".")
        line = to_mdc(line)
      
      test_result_file.write(" ".join(line.split()[1:]) + "\n")
      test_result_id_file.write(line)

      all_test_result_file.write(" ".join(line.split()[1:]) + "\n")
      all_test_result_id_file.write(line)

      all_result_file.write(" ".join(line.split()[1:]) + "\n")

    for lt in file_train:
      line = lt
      if HARMONIZED:
        line = lt.replace(",", ".")
        line = to_mdc(line)
      
      train_result_file.write(" ".join(line.split()[1:]) + "\n")
      train_result_id_file.write(line)

      all_train_result_file.write(" ".join(line.split()[1:]) + "\n")
      all_train_result_id_file.write(line)
    
    for lt in file_val:
      line = lt
      if HARMONIZED:
        line = lt.replace(",", ".")
        line = to_mdc(line)
      
      val_result_file.write(" ".join(line.split()[1:]) + "\n")
      val_result_id_file.write(line)

      all_val_result_file.write(" ".join(line.split()[1:]) + "\n")
      all_val_result_id_file.write(line)
    
    file.close()

    dev_result_file.close()
    train_result_file.close()
    val_result_file.close()
    test_result_file.close()

    dev_result_id_file.close()
    train_result_id_file.close()
    val_result_id_file.close()
    test_result_id_file.close()

  all_result_file.close()
  all_dev_result_file.close()
  all_train_result_file.close()
  all_val_result_file.close()
  all_test_result_file.close()

  all_dev_result_id_file.close()
  all_train_result_id_file.close()
  all_val_result_id_file.close()
  all_test_result_id_file.close()

# extract sentences
print("Extracting sentences...")
extract_sentences("_sentences.txt")

# clean sentences
print("Cleaning sentences...")
clean("_sentences.txt", "_cleaned.txt")

# divide sentences into files
print("Dividing sentences...")
divide_sentences_to_files("_sentences_cleaned.txt")

# get final files
print("Getting final files...")
get_final_files()

# get unique tokens
print("Extracting tokens...")
get_unique_tokens()

# get divide into training, validation and test sets
print("Dividing into training, validation and test sets...")
divide_into_sets()