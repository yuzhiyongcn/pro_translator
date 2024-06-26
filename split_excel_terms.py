import terms_persister as persister
from term_tokenizer import Tokenizer

file_path = r"input\terms-origin.xlsx"
sheet_name = "Sheet1"
term_pairs = persister.read_from_excel(file_path, sheet_name)

# 取前25个术语对
# term_pairs = dict(list(term_pairs.items())[:25])

tokenizer = Tokenizer(term_pairs)
ch2en = tokenizer.get_ch2en()
persister.write_to_excel(ch2en, r"output\terms_zh2en.xlsx")

en2ch = tokenizer.get_en2ch()
persister.write_to_excel(en2ch, r"output\terms_en2zh.xlsx")
