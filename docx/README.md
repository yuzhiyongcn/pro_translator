# DOCX到JSON转换器

这个目录包含了将DOCX文件内容转换为JSON格式的工具。

## 功能特点

- **完整内容提取**: 提取DOCX文件的所有文本内容，包括：
  - 主体段落
  - 表格内容
  - 页眉和页脚
  - 表格中的文本
- **最小片段分割**: 将文本按照最小有意义的片段进行分割
- **JSON格式输出**: 生成格式为 `{"片段":"片段"}` 的JSON文件
- **去重处理**: 自动去除重复的文本片段
- **统计信息**: 显示处理的片段数量

## 文件说明

- `docx_to_json.py`: 主要的转换器类，将DOCX文件转换为JSON
- `json_translator.py`: JSON翻译器，使用GPT-4o-mini将中文翻译为英文
- `json_translator_enhanced.py`: 增强版JSON翻译器，强力迭代翻译所有中文
- `docx_translator_complete.py`: 完整DOCX翻译程序，包含三个步骤
- `example_usage.py`: 使用示例脚本
- `test_converter.py`: DOCX转换器测试脚本
- `test_json_translator.py`: JSON翻译器测试脚本
- `test_step3_only.py`: 步骤3测试脚本（仅替换DOCX内容）
- `run_enhanced_translator.py`: 运行增强版翻译器脚本
- `check_translation_quality.py`: 检查翻译质量脚本
- `README.md`: 说明文档

## 使用方法

### 方法1：直接运行主程序

```bash
python docx_to_json.py
```

程序会提示您输入DOCX文件路径。

### 方法2：使用示例脚本

```bash
python example_usage.py
```

此脚本会自动搜索项目目录中的DOCX文件，并让您选择要处理的文件。

### 方法3：在代码中使用

```python
from docx_to_json import DocxToJsonConverter

# 创建转换器实例
converter = DocxToJsonConverter()

# 转换文件
result = converter.convert_file("input.docx", "output.json")

# 查看统计信息
print(f"处理了 {len(result)} 个文本片段")
```

## 输出格式

生成的JSON文件格式如下：

```json
{
  "单词1": "单词1",
  "句子片段": "句子片段",
  "完整段落": "完整段落",
  "表格内容": "表格内容"
}
```

## 文本片段提取规则

程序会将文本按照以下规则进行分割：

1. **句子级别**: 按句号、问号、感叹号分割
2. **短语级别**: 按逗号、分号、冒号分割  
3. **单词级别**: 按空格分割
4. **保留层次**: 同时保留单词、短语、句子和段落级别的片段

## 依赖项

- `python-docx`: 用于读取DOCX文件
- `json`: 用于生成JSON输出
- `re`: 用于正则表达式文本处理

## 注意事项

- 程序会自动去除重复的文本片段
- 空白内容会被忽略
- 输出的JSON文件使用UTF-8编码
- 如果未指定输出文件名，会自动生成为 `原文件名_fragments.json`

## JSON翻译器使用方法

### 功能特点

- **批量翻译**: 使用GPT-4o-mini模型批量翻译中文内容
- **智能验证**: 翻译后自动验证是否还含有中文字符
- **重试机制**: 对仍含中文的项目进行重新翻译
- **保留原文**: 保留英文、数字、符号等非中文内容
- **token优化**: 智能分批处理，不超过上下文限制

### 使用方法

```bash
# 方法1：直接运行
python json_translator.py

# 方法2：使用测试脚本
python test_json_translator.py

# 方法3：在代码中使用
from json_translator import JsonTranslator
translator = JsonTranslator()
translator.translate_json_file("input.json", "output.json")
```

### 翻译流程

1. 加载JSON文件并分析内容
2. 提取包含中文的项目  
3. 按token限制分批处理
4. 调用GPT-4o-mini进行翻译
5. 验证翻译结果是否还含中文
6. 对仍含中文的项目重新翻译
7. 保存完整的翻译结果

## 完整DOCX翻译程序

### 功能介绍

完整的DOCX翻译程序包含三个步骤：

1. **步骤1**: 将DOCX文件转换为JSON片段
2. **步骤2**: 使用GPT-4o-mini翻译JSON文件（中文→英文）
3. **步骤3**: 读取翻译JSON，复制原DOCX文件并替换内容

### 使用方法

```bash
# 完整工作流程
python docx_translator_complete.py

# 只测试步骤3（替换DOCX内容）
python test_step3_only.py
```

### 步骤3详细说明

步骤3是最复杂的步骤，实现了：

- **智能文本替换**: 根据翻译JSON精确替换原文
- **全文档覆盖**: 替换主文档段落、表格内容、页眉页脚
- **格式保持**: 保持原文档的格式和布局
- **统计报告**: 显示详细的替换统计信息

### 测试结果示例

```
=== 替换统计 ===
主文档段落替换: 111
表格内容替换: 332  
页眉页脚替换: 0
总替换次数: 443
✓ DOCX内容替换完成
```

## 错误处理

- 如果DOCX文件不存在或无法打开，程序会显示错误信息
- 如果没有找到任何文本内容，程序会提示相应信息
- JSON文件保存失败时会显示错误详情
- 翻译API调用失败时会显示详细错误信息
- 翻译前后数量不匹配时会保留原文并显示警告 


# 翻译word文档
创建一个翻译docx的程序, input file使用 input\source\20250611植物提取物非临床安全性研究.docx
首先调用docx_to_json, 将docx文件分割成字符串片段存入json文件, 然后调用json_translator翻译生成的json文件, 第三步, 读取翻译后的json文件, 复制原始docx文件, 根据翻译后的json文件替换复制后的docx中的文字片段