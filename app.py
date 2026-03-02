import streamlit as st
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Atlas IA MVP", page_icon="🌍")

st.title("🚀 Plataforma Atlas - Camaquã")
st.subheader("Transformando jovens em criadores de IA")

# 2. Configurações na Sidebar
st.sidebar.header("Configurações")
# Nomes exatos dos modelos no Hugging Face (sem espaços)
modelos_disponiveis = {
    "Mistral 7B": "mistralai/Mistral-7B-Instruct-v0.3",
    "Llama 3 (8B)": "meta-llama/Meta-Llama-3-8B-Instruct",
    "Gemma 7B": "google/gemma-7b-it"
}
escolha = st.sidebar.selectbox("Escolha o Cérebro:", list(modelos_disponiveis.keys()))
id_modelo = modelos_disponiveis[escolha]

# 3. Inicialização do Histórico
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Entrada do Usuário
if prompt := st.chat_input("Como posso ajudar Camaquã hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "HF_TOKEN" in st.secrets:
        # URL FORMATADA PARA EVITAR 404
        api_url = f"https://api-inference.huggingface.co/models/{id_modelo}"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        # Prompt simplificado para evitar erros de leitura
        payload = {
            "inputs": f"Responda em Português: {prompt}",
            "parameters": {"max_new_tokens": 250}
        }

        try:
            with st.spinner("Conectando ao cérebro da IA..."):
                response = requests.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    res_json = response.json()
                    # Extrai o texto gerado
                    if isinstance(res_json, list):
                        resposta = res_json[0].get('generated_text', '')
                    else:
                        resposta = res_json.get('generated_text', '')
                    
                    # Remove o prompt da resposta se a IA repetir a pergunta
                    resposta = resposta.replace(f"Responda em Português: {prompt}", "").strip()

                    with st.chat_message("assistant"):
                        st.markdown(resposta)
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                
                elif response.status_code == 503:
                    st.warning("O modelo está carregando. Tente novamente em 30 segundos.")
                elif response.status_code == 404:
                    st.error(f"Erro 404: O modelo '{id_modelo}' não foi encontrado. Tente trocar o modelo na barra lateral.")
                else:
                    st.error(f"Erro {response.status_code}: {response.text}")
                    
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Aguardando configuração do HF_TOKEN nos Secrets.")
