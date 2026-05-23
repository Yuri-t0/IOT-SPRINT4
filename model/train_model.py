"""
Rolé - Modelo de IA: Recomendação de Meio de Transporte
Treina um classificador Random Forest com dados simulados
e salva o modelo para uso pela API.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# ─── 1. GERAÇÃO DE DADOS DE TREINO ───────────────────────────────────────────
# Simula histórico de participações do app Rolé
np.random.seed(42)
N = 500

def gerar_transporte(distancia, horario, chuva, lotacao):
    """Regra de negócio para gerar o label correto no dataset."""
    if distancia <= 1.0:
        return "a pé"
    elif distancia <= 3.0 and not chuva:
        return "metrô" if lotacao < 0.7 else "uber"
    elif distancia <= 8.0:
        if chuva:
            return "uber"
        return np.random.choice(["metrô", "ônibus"], p=[0.6, 0.4])
    else:
        if horario >= 22 or horario <= 6:
            return "uber"
        return np.random.choice(["carro", "uber"], p=[0.5, 0.5])

distancias   = np.round(np.random.exponential(scale=5, size=N).clip(0.2, 30), 1)
horarios     = np.random.randint(6, 24, size=N)
chuvas       = np.random.choice([True, False], size=N, p=[0.3, 0.7])
lotacoes     = np.round(np.random.uniform(0, 1, size=N), 2)   # 0 = vazio, 1 = lotado
n_amigos     = np.random.randint(1, 10, size=N)

labels = [
    gerar_transporte(d, h, c, l)
    for d, h, c, l in zip(distancias, horarios, chuvas, lotacoes)
]

df = pd.DataFrame({
    "distancia_km":   distancias,
    "horario":        horarios,
    "chuva":          chuvas.astype(int),
    "lotacao_transporte": lotacoes,
    "n_amigos":       n_amigos,
    "transporte":     labels
})

print("=== Dataset gerado ===")
print(df["transporte"].value_counts())
print()

# ─── 2. PRÉ-PROCESSAMENTO ────────────────────────────────────────────────────
le = LabelEncoder()
df["transporte_enc"] = le.fit_transform(df["transporte"])

FEATURES = ["distancia_km", "horario", "chuva", "lotacao_transporte", "n_amigos"]
X = df[FEATURES]
y = df["transporte_enc"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ─── 3. TREINAMENTO ──────────────────────────────────────────────────────────
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# ─── 4. AVALIAÇÃO ────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print("=== Avaliação do Modelo ===")
print(f"Acurácia: {acc:.2%}")
print()
print(classification_report(y_test, y_pred, target_names=le.classes_))

# ─── 5. SALVANDO MODELO ──────────────────────────────────────────────────────
os.makedirs("model", exist_ok=True)

with open("model/modelo_transporte.pkl", "wb") as f:
    pickle.dump(clf, f)

with open("model/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print("✅ Modelo salvo em model/modelo_transporte.pkl")
print("✅ LabelEncoder salvo em model/label_encoder.pkl")
