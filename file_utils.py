import json


def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # 读取文件内容
            content = file.read()
            # 解析 JSON 数据
            data = json.loads(content)
            return data
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
    except Exception as e:
        print(f"读取文件时出错: {e}")
