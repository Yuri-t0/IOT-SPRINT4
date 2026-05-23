# 🎉 Rolé — IA de Recomendação de Transporte

**Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA  
**Sprint:** 4  
**Integrantes:**
- Adão Yuri Ferreira da Silva — RM 559223
- João Vitor Lopes Santana — RM 560781

---

## 📌 Sobre o Projeto

O **Rolé** é um aplicativo social para coordenação de encontros presenciais entre amigos. A IA integrada nesta sprint **recomenda o meio de transporte ideal** para cada participante com base em variáveis contextuais, eliminando a dúvida de "como vou chegar lá?".

---

## 🤖 Modelo de Inteligência Artificial

### Problema resolvido
Dado um participante e as condições do momento, qual é o melhor meio de transporte para ele chegar ao rolê?

### Tipo de modelo
**Random Forest Classifier** — algoritmo de aprendizado supervisionado baseado em múltiplas árvores de decisão.

### Features de entrada

| Feature | Tipo | Descrição |
|---|---|---|
| `distancia_km` | float | Distância em km até o local do rolê |
| `horario` | int | Hora do dia (0–23) |
| `chuva` | int | 0 = sem chuva, 1 = com chuva |
| `lotacao_transporte` | float | Estimativa de lotação do transporte público (0–1) |
| `n_amigos` | int | Número de amigos no mesmo grupo |

### Classes de saída
`a pé` · `metrô` · `ônibus` · `uber` · `carro`

### Resultados do treinamento
- **Acurácia:** 84%
- **Dataset:** 500 registros simulados com base em regras de negócio reais
- **Split:** 80% treino / 20% teste

---

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────┐
│                    Oracle APEX                          │
│  (Formulário de participação no Rolê)                   │
│  Campos: distância, horário, chuva, lotação, n_amigos   │
└───────────────────────┬─────────────────────────────────┘
                        │ POST /recomendar (JSON)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  API REST (Flask/Python)                 │
│  Recebe JSON → processa → retorna recomendação          │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│            Modelo Random Forest (.pkl)                  │
│  Saída: meio de transporte + probabilidades             │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura do Projeto

```
role-ia/
├── model/
│   ├── train_model.py          # Script de treinamento
│   ├── modelo_transporte.pkl   # Modelo treinado
│   └── label_encoder.pkl       # Encoder das classes
├── api/
│   ├── app.py                  # API Flask
│   └── model/                  # Modelos usados pela API
├── tests/
│   └── test_api.py             # Testes automatizados
└── README.md
```

---

## 🚀 Como Executar

### Pré-requisitos
```bash
pip install flask scikit-learn pandas numpy
```

### 1. Treinar o modelo
```bash
python model/train_model.py
```

### 2. Iniciar a API
```bash
python api/app.py
# API disponível em http://localhost:5000
```

### 3. Rodar os testes
```bash
python tests/test_api.py
```

---

## 🔌 Integração com Oracle APEX

1. Acesse [apex.oracle.com](https://apex.oracle.com) e crie uma conta gratuita
2. Crie um workspace e importe o DDL (`DDL Completo.txt`)
3. Em **Shared Components → Web Source Modules**, configure:
   - URL: `http://<seu-servidor>:5000/recomendar`
   - Método: `POST` / Content-Type: `application/json`
4. No processo da página, envie o payload:

```json
{
  "distancia_km":       :P_DISTANCIA,
  "horario":            :P_HORARIO,
  "chuva":              :P_CHUVA,
  "lotacao_transporte": :P_LOTACAO,
  "n_amigos":           :P_N_AMIGOS
}
```

5. Exiba o campo `recomendacao` do retorno no formulário

---

## 📡 Documentação da API

### `POST /recomendar`

**Request:**
```json
{
  "distancia_km": 4.5,
  "horario": 20,
  "chuva": 0,
  "lotacao_transporte": 0.5,
  "n_amigos": 3
}
```

**Response:**
```json
{
  "status": "ok",
  "recomendacao": "metrô",
  "probabilidades": {
    "a pé": 0.01,
    "carro": 0.04,
    "metrô": 0.52,
    "ônibus": 0.38,
    "uber": 0.05
  }
}
```

---

## 🧪 Evidências de Testes

| Cenário | Distância | Hora | Chuva | Recomendação | Confiança |
|---|---|---|---|---|---|
| Perto, sem chuva | 0.8km | 18h | Não | **a pé** | 91% |
| Longe, noite chuvosa | 15km | 23h | Sim | **uber** | 83% |
| Distância média | 4km | 19h | Não | **metrô** | 52% |
| Grupo grande | 12km | 15h | Não | **uber** | 77% |

---

## 🔗 Links

- 🎥 Vídeo: *(adicionar link do YouTube)*
- 💻 GitHub: https://github.com/JoaoSantana17/roleapl
