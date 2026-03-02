import streamlit as st
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Atlas IA MVP", page_icon="🌍")

st.title("🚀 Plataforma Atlas - Camaquã")
st.subheader("Transformando jovens em criadores de IA")

# 2. Configurações na Sidebar
st.sidebar.header("Configurações")
modelo = st.sidebar.selectbox("Escolha o Cérebro:", 
                              ["mistralai/Mistral-7B-Instruct-v0.3", 
                               "meta-llama/Meta-Llama-3-8B-Instruct"])

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

    # 5. Lógica de Conexão com a nova URL do Hugging Face
    if "HF_TOKEN" in st.secrets:
        # URL EXIGIDA PELO ERRO 410
        api_url = f"https://router.huggingface.co/hf-inference/models/{modelo}"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        instrucao = "Você é um Agente da Plataforma Atlas em Camaquã/RS. Responda de forma curta e em Português."
        payload = {
            "inputs": f"<s>[INST] {instrucao} {prompt} [/INST]",
            "parameters": {"max_new_tokens": 250, "temperature": 0.7}
        }

        try:
            with st.spinner("Conectando ao cérebro da IA..."):
                response = requests.post(api_url, headers=headers, json=payload)
                
                # Verifica se a resposta é JSON válido
                if response.status_code == 200:
                    res_json = response.json()
                    # A nova API pode retornar uma lista ou um dicionário direto
                    if isinstance(res_json, list):
                        resposta = res_json[0].get('generated_text', '').split("[/INST]")[-1].strip()
                    else:
                        resposta = res_json.get('generated_text', '').split("[/INST]")[-1].strip()
                    
                    if not resposta:
                         resposta = "Recebi sua mensagem, mas estou processando a melhor forma de responder. Pode repetir?"

                    with st.chat_message("assistant"):
                        st.markdown(resposta)
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                
                elif response.status_code == 503:
                    st.warning("O modelo está carregando no servidor. Tente novamente em 20 segundos.")
                else:
                    st.error(f"Erro {response.status_code}: {response.text}")
                    
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Aguardando configuração do HF_TOKEN nos Secrets do Streamlit.")
