import codecs
import pandas as pd
import numpy as np
import spacy
import joblib


class PatientExpressionsCoupus:
    def __init__(self) -> None:
        self.df = {}
        self.da = DependencyAnalysis()

    def get_symptom_expressions(self, desease: str) -> list[str]:
        """
        病名に紐づく患者表現一覧を取得する
        """
        expressions = self.df[self.df["標準病名"] == desease]["出現形"].tolist()
        return expressions

    def get_symptom_deps(self, desease: str) -> list[str]:
        """
        病名に紐づく係り受け構文を取得する
        """
        deps = self.df[self.df["標準病名"] == desease]["deps"].tolist()
        return deps

    def get_deseases(self, expression: str) -> list[str]:
        """
        患者表現に紐づく病名を取得する
        """
        deps = self.da.run(expression)
        deseases = self.df[self.df["deps"] == ",".join(deps)]["標準病名"].tolist()
        return deseases

    def analyze(self, text: str) -> str:
        """
        患者表現を係り受け解析して検索のkeyになるようにstringに変換して返す
        """
        deps = self.da.run(text)
        if len(deps) == 0:
            return np.NaN
        return ",".join(deps)

    def load_from_csv(self, file) -> None:
        """
        患者表現辞書をpands.DataFrameに変換
        """
        self.da = DependencyAnalysis()
        with codecs.open(file) as f:
            df = pd.read_table(f, delimiter=",")

        df = df.loc[:, ["出現形", "標準病名"]]
        df["deps"] = df.apply(lambda x: self.analyze(x["出現形"]), axis=1)
        df = df.dropna(how="any")
        self.df = df

    def load(self, file: str) -> None:
        with open(file, mode="rb") as f:
            self.df = joblib.load(f)

    def output(self, file: str) -> None:
        with open(file, mode="wb") as f:
            joblib.dump(
                self.df,
                f,
                compress=3,
            )


class DependencyAnalysis:
    def __init__(self) -> None:
        self.nlp = spacy.load("ja_ginza")

    def run(self, text: str) -> dict[str, str]:
        """
        体の部位を含む主語-名詞,関節目的語の構文を抽出します。
        """

        doc = self.nlp(text)

        ent_words = []
        for ent in doc.ents:
            if ent.label_ == "Animal_Part":
                ent_words.append(ent.text)

        deps = []
        for sent in doc.sents:
            for token in sent:
                if (
                    token.dep_ in ["nsubj", "iobj"]
                    and token.lemma_ in ent_words
                    and len(sent) >= token.head.i
                ):
                    deps.append(f"{token.lemma_}->{sent[token.head.i].lemma_}")

        return deps
