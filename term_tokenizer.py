"""
术语分词器, 将原始的术语对分割成更小的词语
process方法接受一个dict, key和value的关系由term_pair_type确定, term_pair_type是枚举类型, 有两个值, 一个是CH_EN, 一个是EN_CH
输出是两个dict, 一个是中文to英文, 一个是英文to中文
"""

# 术语对类型
from enum import Enum
from gpt_wrapper import GPTWrapper
import ast


class TermPairType(Enum):
    CH_EN = 0
    EN_CH = 1


class Tokenizer:
    def __init__(self, term_pairs, term_pair_type=TermPairType.CH_EN):
        self.gpt = GPTWrapper("gpt-4o")
        system_prompt = """
        You are a professional translator. You are asked to split the long term pair into smaller words.
        I will provide you with the term pairs in json format. e.g. {"中文": "Chinese", "白色狐狸": "white fox"}.
        If you think the term pair is not splittable, you can return the original term pair.
        If i provide {English : Chinese} you should return the same format {English : Chinese}, wise versa.
        If you have a better translation than i provided in value of the key value pair, you can return the better translation.
        Keep numbers or units of measure e.g. length, volume, capacity, density, etc in English. e.g. "1ml" should keep unchanged to "1ml".
        Please reply with the term pairs in pure json format. e.g. {"中文": "Chinese", "白色": "white", "狐狸": "fox"}. No extra characters are allowed.
        Only keep specialized terms related to the biopharmaceutical industry or words with multiple meanings that are easily confused in translation. Delete common word pairs, for example, delete {"食品":"food"}.
        Do not wrap the json with any characters(e.g. ```json ```), just the json format.
        """
        self.gpt.set_system_prompt(system_prompt)

        self.term_pairs = term_pairs
        self.term_pair_type = term_pair_type
        self.ch2en = {}
        self.en2ch = {}
        self._process()

    def _process(self):
        if self.term_pair_type == TermPairType.CH_EN:
            self.ch2en, splittable_ch2en = self._preprocess()
            splitted_ch2en = self._split(splittable_ch2en)
            self.ch2en.update(splitted_ch2en)
            self.en2ch = {v: k for k, v in self.ch2en.items()}
        else:
            self.en2ch, splittable_en2ch = self._preprocess()
            splitted_en2ch = self._split(splittable_en2ch)
            self.en2ch.update(splitted_en2ch)
            self.ch2en = {v: k for k, v in self.en2ch.items()}

    def get_ch2en(self):
        return self.ch2en

    def get_en2ch(self):
        return self.en2ch

    # 过滤长度较大的术语对, 较大的术语对才参与分割, 较小的保留原始的术语对
    def _preprocess(self):
        splittable = {}
        term_pairs = self.term_pairs
        if self.term_pair_type == TermPairType.CH_EN:
            ch2en = {}
            for ch, en in term_pairs.items():
                if len(ch) > 5:  # 中文长度大于4的才可以分割
                    splittable[ch] = en
                else:
                    ch2en[ch] = en
            return ch2en, splittable
        else:
            en2ch = {}
            for en, ch in term_pairs.items():
                # 英文单词数目大于4的才可以分割
                if len(en.split(" ")) > 5:
                    splittable[en] = ch
                else:
                    en2ch[en] = ch
            return en2ch, splittable

    def _split_dict(self, original_dict, chunk_size):
        # 获取字典的项，并转换为列表
        items = list(original_dict.items())

        # 使用列表切片来分割原始字典的项
        chunked_dicts = [
            dict(items[i : i + chunk_size]) for i in range(0, len(items), chunk_size)
        ]

        return chunked_dicts

    # 分割术语对
    def _split(self, splittable):
        print(f"需要分割的术语对数量为: {len(splittable)}")
        # splittable 分割成长度为10的多个字典
        chunked_dicts = self._split_dict(splittable, 10)
        # chunked_dicts = splittable
        splitted = {}
        count = 0
        for dic in chunked_dicts:
            count += 1
            try:
                result = self.gpt.query(f"{dic}")
                result = ast.literal_eval(result)
                splitted.update(result)
                print(f"第{count}次查询成功")
            except Exception as e:
                print(f"### 第{count}次查询失败 ###")

        return splitted


if __name__ == "__main__":
    term_pairs = {
        "大体解剖、脏器称量和组织病理学检查": "Gross Necropsy, Organ Weighing and Histopathological Examination",
        "试验机构": "test facility",
    }
    tokenizer = Tokenizer(term_pairs)
    ch2en = tokenizer.get_ch2en()
    en2ch = tokenizer.get_en2ch()
    print(ch2en)
    print(en2ch)
