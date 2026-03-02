import streamlit as st
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Atlas IA MVP", page_icon="🌍")

st.title("🚀 Plataforma Atlas - Camaquã")
st.subheader("Transformando jovens em criadores de IA")

# 2. Configurações na Sidebar
st.sidebar.header("Configurações")
# Lista de modelos atualizada com base na disponibilidade atual do HF
modelos_disponiveis = {
    "Qwen 2.5 7B (Mais Estável)": "Qwen/Qwen2.5-7B-Instruct",
    "Mistral 7B v0.3": "mistralai/Mistral-7B-Instruct-v0.3",
    "Gemma 2 9B": "google/gemma-2-9b-it"
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
        # Usando a URL do Router que é o novo padrão exigido
        api_url = f"https://router.huggingface.co/hf-inference/models/{id_modelo}"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        payload = {
            "inputs": f"<|im_start|>system\nVocê é o Agente Atlas, um assistente educativo para Camaquã/RS. Responda em Português.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n",
            "parameters": {"max_new_tokens": 500, "temperature": 0.7}
        }

        try:
            with st.spinner("Conectando ao Atlas..."):
                response = requests.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    res_json = response.json()
                    # Extração de texto para o modelo Qwen/Mistral
                    if isinstance(res_json, list):
                        resposta = res_json[0].get('generated_text', '')
                    else:
                        resposta = res_json.get('generated_text', '')
                    
                    # Limpeza para mostrar apenas a fala da IA
                    if "assistant\n" in resposta:
                        resposta = resposta.split("assistant\n")[-1].strip()
                    
                    with st.chat_message("assistant"):
                        st.markdown(resposta)
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                
                elif response.status_code == 503:
                    st.warning("IA carregando... Aguarde 15 segundos e tente enviar novamente.")
                elif response.status_code == 404:
                    st.error(f"Modelo {id_modelo} não encontrado na API gratuita. Tente outro modelo na barra lateral.")
                else:
                    st.error(f"Erro {response.status_code}: {response.text}")
                    
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Verifique o HF_TOKEN nos Secrets do Streamlit.")
