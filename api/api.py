"""
Rolé - API REST de Recomendação de Transporte
Sprint 4 - DISRUPTIVE ARCHITECTURES: IOT, IOB & GENERATIVE IA

Endpoints:
  POST /recomendar  → recebe dados e retorna recomendação
  GET  /health      → verifica se a API está no ar
  GET  /exemplos    → retorna exemplos de uso

Como rodar:
  pip install flask flask-cors scikit-learn pandas joblib
  python api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Permite chamadas do Oracle APEX

# ─── Carrega o modelo ─────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../modelo/modelo_transporte.pkl")
modelo = joblib.load(MODEL_PATH)

FEATURES = ["distancia_km", "hora_do_dia", "chuva", "num_pessoas_no_role", "pressa"]

DESCRICOES = {
    "a pé":    "Destino próximo! Vá a pé, é rápido e saudável.",
    "uber":    "Melhor chamar um Uber — confortável e direto.",
    "metrô":   "Pegue o metrô, é a opção mais rápida e barata.",
    "ônibus":  "Ônibus é a melhor opção para essa distância.",
    "carro":   "Vale ir de carro — a distância justifica."
}

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "modelo": "RandomForestClassifier", "versao": "1.0"})


@app.route("/recomendar", methods=["POST"])
def recomendar():
    """
    Body JSON esperado:
    {
        "distancia_km": 5.0,
        "hora_do_dia": 19,
        "chuva": 1,
        "num_pessoas_no_role": 8,
        "pressa": 1
    }
    """
    try:
        body = request.get_json(force=True)

        # Validação dos campos
        campos_faltando = [f for f in FEATURES if f not in body]
        if campos_faltando:
            return jsonify({
                "erro": f"Campos obrigatórios ausentes: {campos_faltando}",
                "campos_necessarios": FEATURES
            }), 400

        # Validações de range
        if not (0 <= float(body["distancia_km"]) <= 200):
            return jsonify({"erro": "distancia_km deve estar entre 0 e 200"}), 400
        if not (0 <= int(body["hora_do_dia"]) <= 23):
            return jsonify({"erro": "hora_do_dia deve estar entre 0 e 23"}), 400
        if int(body["chuva"]) not in [0, 1]:
            return jsonify({"erro": "chuva deve ser 0 (não) ou 1 (sim)"}), 400
        if int(body["pressa"]) not in [0, 1]:
            return jsonify({"erro": "pressa deve ser 0 (não) ou 1 (sim)"}), 400

        entrada = pd.DataFrame([{
            "distancia_km":        float(body["distancia_km"]),
            "hora_do_dia":         int(body["hora_do_dia"]),
            "chuva":               int(body["chuva"]),
            "num_pessoas_no_role": int(body["num_pessoas_no_role"]),
            "pressa":              int(body["pressa"])
        }])

        recomendacao = modelo.predict(entrada)[0]
        probabilidades = modelo.predict_proba(entrada)[0]
        confianca = round(float(max(probabilidades)) * 100, 1)

        # Todas as probabilidades por classe
        classes_prob = {
            cls: round(float(prob) * 100, 1)
            for cls, prob in zip(modelo.classes_, probabilidades)
        }

        return jsonify({
            "recomendacao":   recomendacao,
            "confianca_pct":  confianca,
            "descricao":      DESCRICOES.get(recomendacao, ""),
            "probabilidades": classes_prob,
            "entrada_recebida": {
                "distancia_km":        float(body["distancia_km"]),
                "hora_do_dia":         int(body["hora_do_dia"]),
                "chuva":               bool(int(body["chuva"])),
                "num_pessoas_no_role": int(body["num_pessoas_no_role"]),
                "pressa":              bool(int(body["pressa"]))
            }
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/exemplos", methods=["GET"])
def exemplos():
    return jsonify({
        "exemplos": [
            {
                "descricao": "Perto, sem chuva, sem pressa",
                "input": {"distancia_km": 0.5, "hora_do_dia": 14, "chuva": 0, "num_pessoas_no_role": 3, "pressa": 0},
                "esperado": "a pé"
            },
            {
                "descricao": "Médio, com chuva, com pressa",
                "input": {"distancia_km": 5.0, "hora_do_dia": 19, "chuva": 1, "num_pessoas_no_role": 8, "pressa": 1},
                "esperado": "uber"
            },
            {
                "descricao": "Longe, sem chuva, sem pressa",
                "input": {"distancia_km": 30.0, "hora_do_dia": 22, "chuva": 0, "num_pessoas_no_role": 12, "pressa": 0},
                "esperado": "carro"
            }
        ]
    })


if __name__ == "__main__":
    print("🚀 API do Rolé rodando em http://localhost:5000")
    print("   POST /recomendar  → recomendação de transporte")
    print("   GET  /health      → status da API")
    print("   GET  /exemplos    → exemplos de uso")
    app.run(debug=True, host="0.0.0.0", port=5000)
