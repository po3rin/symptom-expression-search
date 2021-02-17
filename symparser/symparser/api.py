import uvicorn
import json
from fastapi import FastAPI, Body
from elasticsearch import Elasticsearch
from symparser.core import DependencyAnalysis, PatientExpressionsCoupus


app = FastAPI()
es = Elasticsearch("http://localhost:9200")

pec = PatientExpressionsCoupus()
pec.load("symptoms_expression_dict.joblib")


@app.get("/topics/search")
def topics(q: str = None):
    deseases = pec.get_deseases(q)

    deps = []
    for d in deseases:
        deps.extend(pec.get_symptom_deps(d))

    expression_queries = [{"match": {"deps": e}} for e in deps]

    if len(expression_queries) == 0:
        return {}

    query = {
        "query": {"bool": {"should": expression_queries, "minimum_should_match": 1}}
    }
    q = json.dumps(query)

    return es.search(index="topics", body=query, size=3)


@app.post("/topics")
def topics(body: dict = Body(None)):
    d = DependencyAnalysis()
    deps = d.run(body["title"])

    topic = {
        "id": body["id"],
        "title": body["title"],
        "deps": deps,
    }

    # ドキュメントの登録
    return es.create(id=body["id"], index="topics", body=topic)


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
