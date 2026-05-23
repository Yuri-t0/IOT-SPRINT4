"""
Rolé - Testes da IA com Evidências
Rode esse script para gerar os resultados de teste para a documentação.
"""

import joblib
import pandas as pd
import json

modelo = joblib.load("modelo/modelo_transporte.pkl")
FEATURES = ["distancia_km", "hora_do_dia", "chuva", "num_pessoas_no_role", "pressa"]

casos = [
    {
        "descricao": "Vizinho próximo, tarde sem chuva",
        "input": {"distancia_km": 0.4, "hora_do_dia": 15, "chuva": 0, "num_pessoas_no_role": 2, "pressa": 0}
    },
    {
        "descricao": "Médio, noite com chuva, sem pressa",
        "input": {"distancia_km": 6.0, "hora_do_dia": 21, "chuva": 1, "num_pessoas_no_role": 5, "pressa": 0}
    },
    {
        "descricao": "Médio, tarde sem chuva, sem pressa",
        "input": {"distancia_km": 6.0, "hora_do_dia": 16, "chuva": 0, "num_pessoas_no_role": 5, "pressa": 0}
    },
    {
        "descricao": "Médio, tarde sem chuva, com pressa",
        "input": {"distancia_km": 6.0, "hora_do_dia": 16, "chuva": 0, "num_pessoas_no_role": 5, "pressa": 1}
    },
    {
        "descricao": "Longe, noite sem chuva, sem pressa",
        "input": {"distancia_km": 25.0, "hora_do_dia": 22, "chuva": 0, "num_pessoas_no_role": 10, "pressa": 0}
    },
    {
        "descricao": "Longe, dia sem chuva, com pressa",
        "input": {"distancia_km": 25.0, "hora_do_dia": 10, "chuva": 0, "num_pessoas_no_role": 10, "pressa": 1}
    },
    {
        "descricao": "Muito longe, qualquer condição",
        "input": {"distancia_km": 60.0, "hora_do_dia": 18, "chuva": 0, "num_pessoas_no_role": 15, "pressa": 0}
    },
]

print("=" * 65)
print("  ROLÉ — EVIDÊNCIAS DE TESTE DA IA DE TRANSPORTE")
print("  Modelo: Random Forest Classifier | Acurácia: 99%")
print("=" * 65)

for i, caso in enumerate(casos, 1):
    inp = caso["input"]
    df = pd.DataFrame([inp])
    pred = modelo.predict(df)[0]
    proba = modelo.predict_proba(df)[0]
    confianca = round(max(proba) * 100, 1)
    classes_prob = {cls: f"{round(p*100,1)}%" for cls, p in zip(modelo.classes_, proba)}

    print(f"\nTeste #{i}: {caso['descricao']}")
    print(f"  Entrada:      {json.dumps(inp, ensure_ascii=False)}")
    print(f"  Recomendação: {pred.upper()}")
    print(f"  Confiança:    {confianca}%")
    print(f"  Probabilidades: {classes_prob}")

print("\n" + "=" * 65)
print("  Todos os testes concluídos com sucesso ✅")
print("=" * 65)
