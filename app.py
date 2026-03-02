import streamlit as st
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Atlas IA MVP", page_icon="🌍")

st.title("🚀 Plataforma Atlas - Camaquã")
st.subheader("Transformando jovens em criadores de IA")

# 2. Configurações na Sidebar
st.sidebar.header("Configurações")
modelos_disponiveis = {
    "Gemma 7B (Recomendado)": "google/gemma-7b-it",
    "Mistral 7B": "mistralai/Mistral-7B-Instruct-v0.3",
    "Llama 3": "meta-llama/Meta-Llama-3-8B-Instruct"
}
escolha = st.sidebar.selectbox("Escolha o Cérebro:", list(modelos_disponiveis.keys()))
id_modelo = modelos_disponiveis[escolha]

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso ajudar Camaquã hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "HF_TOKEN" in st.secrets:
        api_url = f"https://router.huggingface.co/hf-inference/models/{id_modelo}"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        payload = {
            "inputs": f"Instrução: Você é o Agente Atlas de Camaquã. Responda em Português.\nUsuário: {prompt}\nAssistente:",
            "parameters": {"max_new_tokens": 300, "return_full_text": False}
        }

        try:
            with st.spinner("Conectando ao Atlas..."):
                response = requests.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 404:
                    api_url_fallback = f"https://api-inference.huggingface.co/models/{id_modelo}"
                    response = requests.post(api_url_fallback, headers=headers, json=payload)

                if response.status_code == 200:
                    res_json = response.json()
                    resposta = res_json[0].get('generated_text', '') if isinstance(res_json, list) else res_json.get('generated_text', '')
                    with st.chat_message("assistant"):
                        st.markdown(resposta)
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                elif response.status_code == 503:
                    st.warning("O modelo está acordando. Tente novamente em 15 segundos.")
                else:
                    st.error(f"Erro {response.status_code}: {response.text}")
                    
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Verifique o HF_TOKEN nos Secrets do Streamlit.")
