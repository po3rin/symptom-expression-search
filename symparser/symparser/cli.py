import json
import argparse
from symparser.core import DependencyAnalysis, PatientExpressionsCoupus

parser = argparse.ArgumentParser(description="Parsing patient expression of symptoms")

parser.add_argument(
    "-t",
    "--txt",
    required=True,
    help="symptom expression",
)

# parser.add_argument(
#     "-r",
#     "--row_corpus",
#     help="patient expression dict file (csv)",
# )

parser.add_argument(
    "-c",
    "--corpus",
    default="symptoms_expression_dict.joblib",
    help="patient expression dict file (joblib dump)",
)


def cli() -> None:
    args = parser.parse_args()
    t = args.txt
    c = args.corpus

    pec = PatientExpressionsCoupus()
    # pec.load(c)
    pec.load_from_csv("corpus/D3_20190326.csv")
    pec.output(c)

    d = DependencyAnalysis()
    dep = d.run(t)
    print(dep)

    deseases = pec.get_deseases(t)
    expression_list = []
    print(deseases)
    for d in deseases:
        expression_list.extend(pec.get_symptom_expressions(d))
    print(expression_list)
