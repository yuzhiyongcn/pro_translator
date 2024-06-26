import pandas as pd


def remove_newlines(d):
    cleaned_dict = {}

    for key, value in d.items():
        # 移除键中的换行符
        clean_key = key.replace("\r", "").replace("\n", "")

        # 移除值中的换行符
        clean_value = value.replace("\r", "").replace("\n", "")

        # 更新清理后的键值对到新的字典
        cleaned_dict[clean_key] = clean_value

    return cleaned_dict


def read_from_excel(file_path, sheet_name=0):
    # 读取 Excel 文件
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # 确保 DataFrame 至少有两列
    if df.shape[1] < 2:
        raise ValueError("The Excel file must have at least two columns.")

    # 获取前两列数据
    df = df.iloc[:, :2]

    # 去除重复键中的重复项，保留第一组
    df = df.drop_duplicates(subset=df.columns[0], keep="first")

    # 将 DataFrame 转换为字典
    result_dict = dict(zip(df[df.columns[0]], df[df.columns[1]]))

    return remove_newlines(result_dict)


def write_to_excel(data_dict, file_path):
    # 将字典转换为 DataFrame
    df = pd.DataFrame(list(data_dict.items()))

    # 写入 Excel 文件，不写入列头
    df.to_excel(file_path, header=False, index=False)


if __name__ == "__main__":
    terms = read_from_excel("input/terms_zh2en.xlsx")
    reversed_terms = {v: k for k, v in terms.items()}
    write_to_excel(reversed_terms, "output/terms_en2zh.xlsx")
