# Integração Oracle APEX ↔ API de IA do Rolé

## Pré-requisitos
- Conta no [apex.oracle.com](https://apex.oracle.com) (gratuita)
- API do Rolé rodando (localmente ou em servidor público)
- Para expor a API localmente: usar [ngrok](https://ngrok.com) — `ngrok http 5000`

---

## Passo 1 — Criar a aplicação no APEX

1. Acesse [apex.oracle.com](https://apex.oracle.com) e faça login
2. Clique em **App Builder → Create → New Application**
3. Nome: `Rolé`
4. Adicione uma página do tipo **Form** ou **Blank Page**

---

## Passo 2 — Criar Web Source (conexão com a API)

1. No App Builder, vá em **Shared Components → Web Source Modules**
2. Clique em **Create**
3. Preencha:
   - **Name:** `IA_Transporte`
   - **URL:** `http://SEU_ENDERECO:5000` (ou URL do ngrok)
   - **Method:** POST
   - **Endpoint:** `/recomendar`
4. Em **Parameters**, adicione os campos:
   - `distancia_km` (Number)
   - `hora_do_dia` (Number)
   - `chuva` (Number)
   - `num_pessoas_no_role` (Number)
   - `pressa` (Number)

---

## Passo 3 — Criar a página de recomendação

1. Crie uma nova página **Blank**
2. Adicione os seguintes **Page Items** (campos de entrada):
   - `P1_DISTANCIA` — Number Field — Label: "Distância até o rolê (km)"
   - `P1_HORA` — Number Field — Label: "Hora atual (0-23)"
   - `P1_CHUVA` — Select List — Label: "Está chovendo?" — Values: 0=Não, 1=Sim
   - `P1_PESSOAS` — Number Field — Label: "Pessoas já no rolê"
   - `P1_PRESSA` — Select List — Label: "Está com pressa?" — Values: 0=Não, 1=Sim
3. Adicione um **Button** com label "Recomendar Transporte"
4. Adicione um **Display Only Item** `P1_RESULTADO` para mostrar a resposta

---

## Passo 4 — Criar o processo que chama a API

1. Na página criada, vá em **Processing → Create Process**
2. Tipo: **Invoke API** (ou **Execute Code** com PL/SQL + APEX_WEB_SERVICE)
3. Use o código PL/SQL abaixo:

```sql
DECLARE
  l_url        VARCHAR2(500) := 'http://SEU_ENDERECO:5000/recomendar';
  l_body       CLOB;
  l_response   CLOB;
  l_resultado  VARCHAR2(255);
BEGIN
  -- Monta o JSON de entrada
  l_body := '{'
    || '"distancia_km":'        || :P1_DISTANCIA  || ','
    || '"hora_do_dia":'         || :P1_HORA        || ','
    || '"chuva":'               || :P1_CHUVA       || ','
    || '"num_pessoas_no_role":' || :P1_PESSOAS     || ','
    || '"pressa":'              || :P1_PRESSA
    || '}';

  -- Chama a API
  l_response := apex_web_service.make_rest_request(
    p_url         => l_url,
    p_http_method => 'POST',
    p_body        => l_body,
    p_wallet_path => ''
  );

  -- Extrai o campo "recomendacao" do JSON retornado
  l_resultado := apex_json.get_varchar2(
    p_path   => 'recomendacao',
    p_source => l_response
  );

  -- Exibe para o usuário
  :P1_RESULTADO := '🚗 Recomendação: ' || UPPER(l_resultado);

EXCEPTION
  WHEN OTHERS THEN
    :P1_RESULTADO := 'Erro ao consultar IA: ' || SQLERRM;
END;
```

4. Configure o processo para rodar quando o botão for clicado (condição: `Button = RECOMENDAR`)

---

## Passo 5 — Testar

1. Execute a aplicação no APEX
2. Preencha os campos e clique em **Recomendar Transporte**
3. O campo resultado exibirá a recomendação da IA

**Exemplo de resultado esperado:**
```
🚗 Recomendação: UBER
```

---

## Evidências para a entrega

Registre os seguintes prints para a documentação:
- [ ] API rodando (`GET /health` retornando `{"status": "ok"}`)
- [ ] Chamada `POST /recomendar` com body e resposta no Postman/Insomnia
- [ ] Página do APEX com os campos preenchidos
- [ ] Resultado da recomendação aparecendo no APEX
- [ ] Terminal mostrando o modelo treinado com as métricas

---

## Fluxo completo

```
┌─────────────────────────────────────────────────────────┐
│                    Oracle APEX                          │
│                                                         │
│  [Distância] [Hora] [Chuva] [Pessoas] [Pressa]         │
│                    [Recomendar]                         │
│                                                         │
│  Resultado: 🚗 Recomendação: UBER                       │
└───────────────────┬─────────────────────────────────────┘
                    │ POST /recomendar (JSON)
                    ▼
┌─────────────────────────────────────────────────────────┐
│              API REST (Flask · Python)                  │
│                                                         │
│  Recebe JSON → Monta DataFrame → modelo.predict()       │
│  Retorna: { recomendacao, confianca_pct, descricao }    │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│         Modelo Random Forest (scikit-learn)             │
│                                                         │
│  Features: distancia, hora, chuva, pessoas, pressa      │
│  Classes:  a pé | uber | metrô | ônibus | carro         │
│  Acurácia: 99%                                          │
└─────────────────────────────────────────────────────────┘
```
