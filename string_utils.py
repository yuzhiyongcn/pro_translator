def has_chinese(s):
    for char in s:
        if "\u4e00" <= char <= "\u9fff":
            return True
    return False
