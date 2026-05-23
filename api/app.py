"""
Rolé - API REST de Recomendação de Transporte
Consumível pelo Oracle APEX via Web Source / AJAX
"""

from flask import Flask, request, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# ─── Carrega modelo e encoder ────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "model", "modelo_transporte.pkl")
LE_PATH    = os.path.join(BASE, "model", "label_encoder.pkl")

with open(MODEL_PATH, "rb") as f:
    modelo = pickle.load(f)

with open(LE_PATH, "rb") as f:
    le = pickle.load(f)

# ─── Endpoint principal ───────────────────────────────────────────────────────
@app.route("/recomendar", methods=["POST"])
def recomendar():
    """
    Recebe JSON com dados do participante e retorna recomendação de transporte.

    Body esperado:
    {
        "distancia_km": 5.2,
        "horario": 20,
        "chuva": 0,
        "lotacao_transporte": 0.4,
        "n_amigos": 3
    }

    Retorno:
    {
        "recomendacao": "metrô",
        "probabilidades": { "a pé": 0.01, "carro": 0.05, ... },
        "status": "ok"
    }
    """
    data = request.get_json()

    # Validação dos campos obrigatórios
    campos = ["distancia_km", "horario", "chuva", "lotacao_transporte", "n_amigos"]
    for campo in campos:
        if campo not in data:
            return jsonify({"status": "erro", "mensagem": f"Campo '{campo}' obrigatório"}), 400

    try:
        X = np.array([[
            float(data["distancia_km"]),
            int(data["horario"]),
            int(data["chuva"]),
            float(data["lotacao_transporte"]),
            int(data["n_amigos"])
        ]])

        pred_enc   = modelo.predict(X)[0]
        pred_proba = modelo.predict_proba(X)[0]

        recomendacao  = le.inverse_transform([pred_enc])[0]
        probabilidades = {
            classe: round(float(prob), 4)
            for classe, prob in zip(le.classes_, pred_proba)
        }

        return jsonify({
            "status": "ok",
            "recomendacao": recomendacao,
            "probabilidades": probabilidades
        })

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Healthcheck para o Oracle APEX verificar se a API está online."""
    return jsonify({"status": "ok", "modelo": "RandomForest", "versao": "1.0"})


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "app": "Rolé - IA de Transporte",
        "endpoints": {
            "POST /recomendar": "Recomenda meio de transporte",
            "GET  /health":     "Verifica status da API"
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
