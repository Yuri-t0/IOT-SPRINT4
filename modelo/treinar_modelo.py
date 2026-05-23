"""
Rolé - Modelo de IA: Recomendação de Meio de Transporte
Sprint 4 - DISRUPTIVE ARCHITECTURES: IOT, IOB & GENERATIVE IA

Entradas:
  - distancia_km: distância em km até o evento
  - hora_do_dia: hora (0-23)
  - chuva: 0 ou 1
  - num_pessoas_no_role: quantas pessoas já estão no rolê
  - pressa: 0 (sem pressa) ou 1 (com pressa)

Saída:
  - meio de transporte recomendado: carro, uber, metrô, ônibus, a pé
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# ─── 1. GERAÇÃO DE DADOS SINTÉTICOS ───────────────────────────────────────────
np.random.seed(42)
N = 1000

def gerar_label(row):
    d = row["distancia_km"]
    h = row["hora_do_dia"]
    c = row["chuva"]
    p = row["pressa"]

    if d <= 0.8:
        return "a pé"
    elif d <= 3:
        if c == 1 or p == 1:
            return "uber"
        return "a pé"
    elif d <= 8:
        if c == 1:
            return "uber"
        if 6 <= h <= 22:
            return "metrô"
        return "uber"
    elif d <= 20:
        if p == 1:
            return "uber"
        if 6 <= h <= 22:
            return "ônibus"
        return "carro"
    else:
        if p == 1:
            return "uber"
        return "carro"

data = pd.DataFrame({
    "distancia_km":         np.round(np.random.exponential(scale=10, size=N).clip(0.1, 80), 2),
    "hora_do_dia":          np.random.randint(0, 24, N),
    "chuva":                np.random.randint(0, 2, N),
    "num_pessoas_no_role":  np.random.randint(1, 20, N),
    "pressa":               np.random.randint(0, 2, N),
})
data["transporte"] = data.apply(gerar_label, axis=1)

# ─── 2. TREINO ────────────────────────────────────────────────────────────────
FEATURES = ["distancia_km", "hora_do_dia", "chuva", "num_pessoas_no_role", "pressa"]
TARGET   = "transporte"

X = data[FEATURES]
y = data[TARGET]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# ─── 3. AVALIAÇÃO ─────────────────────────────────────────────────────────────
y_pred = modelo.predict(X_test)
print("=== Relatório de Classificação ===")
print(classification_report(y_test, y_pred))

# ─── 4. SALVAR MODELO ─────────────────────────────────────────────────────────
os.makedirs("modelo", exist_ok=True)
joblib.dump(modelo, "modelo/modelo_transporte.pkl")
print("✅ Modelo salvo em modelo/modelo_transporte.pkl")

# ─── 5. TESTE RÁPIDO ──────────────────────────────────────────────────────────
exemplos = pd.DataFrame([
    {"distancia_km": 0.5,  "hora_do_dia": 14, "chuva": 0, "num_pessoas_no_role": 3,  "pressa": 0},
    {"distancia_km": 5.0,  "hora_do_dia": 19, "chuva": 1, "num_pessoas_no_role": 8,  "pressa": 1},
    {"distancia_km": 30.0, "hora_do_dia": 22, "chuva": 0, "num_pessoas_no_role": 12, "pressa": 0},
])
print("\n=== Previsões de exemplo ===")
for i, row in exemplos.iterrows():
    pred = modelo.predict([row[FEATURES].values])[0]
    proba = modelo.predict_proba([row[FEATURES].values])[0]
    confianca = round(max(proba) * 100, 1)
    print(f"  Distância {row['distancia_km']}km | Chuva={'Sim' if row['chuva'] else 'Não'} | Pressa={'Sim' if row['pressa'] else 'Não'} → {pred} ({confianca}%)")
