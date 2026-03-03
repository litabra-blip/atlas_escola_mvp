from typing import Any

import requests
import streamlit as st

st.set_page_config(page_title="Atlas IA", page_icon="🌍")
st.title("🚀 Plataforma Atlas - Camaquã")

# Modelo com boa taxa de sucesso em tokens gratuitos
ID_MODELO = "mistralai/Mistral-7B-Instruct-v0.2"
TIMEOUT_SEGUNDOS = 60
ENDPOINTS = [
    f"https://router.huggingface.co/hf-inference/models/{ID_MODELO}",
    f"https://api-inference.huggingface.co/models/{ID_MODELO}",
]


def deve_tentar_proximo_endpoint(status_code: int) -> bool:
    """Define quais códigos devem acionar fallback para o próximo endpoint."""
    return status_code in (404, 410, 429, 503)


def consultar_modelo(prompt: str, token: str) -> tuple[requests.Response, str]:
    headers = {"Authorization": f"Bearer {token.strip()}"}
    payload = {
        "inputs": f"<s>[INST] Responda em Português: {prompt} [/INST]",
        "parameters": {"max_new_tokens": 500},
        "options": {"wait_for_model": True},
    }

    ultima_resposta: requests.Response | None = None
    endpoint_usado = ENDPOINTS[0]

    for endpoint in ENDPOINTS:
        tentativa = requests.post(endpoint, headers=headers, json=payload, timeout=TIMEOUT_SEGUNDOS)
        ultima_resposta = tentativa
        endpoint_usado = endpoint

        if not deve_tentar_proximo_endpoint(tentativa.status_code):
            break

    if ultima_resposta is None:
        raise RuntimeError("Nenhuma tentativa de inferência foi executada.")

    return ultima_resposta, endpoint_usado


def extrair_resposta(res_json: dict[str, Any] | list[Any]) -> str:
    output = ""
    if isinstance(res_json, list):
        if res_json and isinstance(res_json[0], dict):
            output = str(res_json[0].get("generated_text", ""))
    elif isinstance(res_json, dict):
        output = str(res_json.get("generated_text", ""))

    resposta = output.split("[/INST]")[-1].strip()
    return resposta or "Não consegui gerar resposta agora. Tente novamente em instantes."


def extrair_detalhe_erro(response: requests.Response) -> str:
    detalhe = response.text
    try:
        body = response.json()
    except ValueError:
        return detalhe

    if isinstance(body, dict):
        if "error" in body:
            return str(body["error"])
        if "message" in body:
            return str(body["message"])

    return detalhe


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso ajudar Camaquã hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "HF_TOKEN" not in st.secrets:
        st.error("Configure o segredo HF_TOKEN no Streamlit Secrets para usar o chat.")
    else:
        try:
            with st.spinner("Conectando ao Atlas..."):
                response, endpoint_usado = consultar_modelo(prompt, st.secrets["HF_TOKEN"])

            if response.status_code == 200:
                try:
                    resposta = extrair_resposta(response.json())
                except ValueError:
                    resposta = "Não consegui interpretar a resposta do modelo. Tente novamente."

                with st.chat_message("assistant"):
                    st.markdown(resposta)
                    st.session_state.messages.append({"role": "assistant", "content": resposta})
            else:
                detalhe = extrair_detalhe_erro(response)
                st.error(
                    f"Erro {response.status_code} no endpoint de inferência. "
                    f"Endpoint: {endpoint_usado}. Detalhe: {detalhe}"
                )
        except requests.RequestException as e:
            st.error(f"Erro de conexão com o serviço de IA: {e}")
