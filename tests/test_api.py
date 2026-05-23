"""
Rolé - Testes da API de Recomendação
Executa chamadas simulando o que o Oracle APEX enviaria.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

casos = [
    {
        "descricao": "Participante perto (0.8km), sem chuva → a pé",
        "payload": {"distancia_km": 0.8, "horario": 18, "chuva": 0, "lotacao_transporte": 0.3, "n_amigos": 2}
    },
    {
        "descricao": "Participante longe (15km), noite chuvosa → uber",
        "payload": {"distancia_km": 15.0, "horario": 23, "chuva": 1, "lotacao_transporte": 0.8, "n_amigos": 1}
    },
    {
        "descricao": "Distância média (4km), horário normal, sem chuva → metrô",
        "payload": {"distancia_km": 4.0, "horario": 19, "chuva": 0, "lotacao_transporte": 0.4, "n_amigos": 4}
    },
    {
        "descricao": "Grupo grande (8 amigos), distância média → carro",
        "payload": {"distancia_km": 12.0, "horario": 15, "chuva": 0, "lotacao_transporte": 0.2, "n_amigos": 8}
    },
    {
        "descricao": "Teste de erro - campo faltando",
        "payload": {"distancia_km": 5.0, "horario": 20}
    }
]

print("=" * 60)
print("  ROLÉ — Testes da API de Recomendação de Transporte")
print("=" * 60)

for i, caso in enumerate(casos, 1):
    print(f"\n[Teste {i}] {caso['descricao']}")
    print(f"  Input:  {json.dumps(caso['payload'])}")
    try:
        r = requests.post(f"{BASE_URL}/recomendar", json=caso["payload"], timeout=5)
        resultado = r.json()
        if resultado.get("status") == "ok":
            print(f"  ✅ Recomendação: {resultado['recomendacao'].upper()}")
            probs = resultado["probabilidades"]
            top = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"  Top probabilidades: {', '.join(f'{k}: {v:.0%}' for k, v in top)}")
        else:
            print(f"  ⚠️  Erro esperado: {resultado.get('mensagem')}")
    except Exception as e:
        print(f"  ❌ Falha na conexão: {e}")

print("\n" + "=" * 60)
print("  Healthcheck")
print("=" * 60)
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"  Status: {r.json()}")
except Exception as e:
    print(f"  ❌ {e}")
