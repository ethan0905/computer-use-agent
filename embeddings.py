import numpy as np
import openai
from config import OPENAI_API_KEY

CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str, engine: str = "text-embedding-ada-002") -> list[float]:
    resp = CLIENT.embeddings.create(model=engine, input=[text])
    return resp.data[0].embedding  # type: ignore

def distances_from_embeddings(target: list[float], others: list[list[float]]) -> list[float]:
    t = np.array(target)
    t_norm = np.linalg.norm(t)
    res = []
    for vec in others:
        v = np.array(vec)
        norm_v = np.linalg.norm(v)
        if t_norm == 0 or norm_v == 0:
            res.append(1.0)
        else:
            cos = float(np.dot(t, v) / (t_norm * norm_v))
            res.append(1.0 - cos)
    return res
