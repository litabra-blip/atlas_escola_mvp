import streamlit as st
import requests
import time

# Configuração Visual
st.set_page_config(page_title="Atlas IA MVP", page_icon="🌍")

st.title("🚀 Plataforma Atlas - Camaquã")
st.subheader("Transformando jovens em criadores de IA")

# Sidebar
st.sidebar.header("Configurações")
modelo = st.sidebar.selectbox("Escolha o Cérebro:", 
                              ["mistralai/Mistral-7B-Instruct-v0.3", 
                               "meta-llama/Meta-Llama-3-8B-Instruct"])

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
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        api_url = f"https://api-inference.huggingface.co/models/{modelo}" # Voltando para a URL padrão que estabilizou
        
        instrucao = "Você é um Agente da Plataforma Atlas em Camaquã/RS. Responda em Português."
        payload = {"inputs": f"{instrucao}\nUsuário: {prompt}\nAgente:", "parameters": {"max_new_tokens": 500}}

        try:
            with st.spinner("IA pensando..."):
                response = requests.post(api_url, headers=headers, json=payload)
                
                # Se a resposta não for JSON, pegamos o erro de texto
                try:
                    response_json = response.json()
                except:
                    st.error(f"Erro no formato da resposta: {response.text}")
                    st.stop()

                if response.status_code == 200:
                    res_text = response_json[0]['generated_text'] if isinstance(response_json, list) else response_json['generated_text']
                    resposta = res_text.split("Agente:")[-1].strip()
                    with st.chat_message("assistant"):
                        st.markdown(resposta)
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                
                elif "estimated_time" in str(response_json):
                    st.warning("O 'cérebro' da IA está acordando. Aguarde 20 segundos e tente enviar novamente.")
                else:
                    st.error(f"Erro {response.status_code}: {response_json}")
        except Exception as e:
            st.error(f"Erro na conexão: {e}")
    else:
        st.warning("Configure o HF_TOKEN nos Secrets.")
