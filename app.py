import streamlit as st
import requests

# Configuração Visual alinhada à Plataforma Atlas
st.set_page_config(page_title="Atlas IA MVP", page_icon="🌍")

st.title("🚀 Plataforma Atlas - Camaquã")
st.subheader("Transformando jovens em criadores de IA")

# Sidebar para configurações
st.sidebar.header("Configurações do Agente")
modelo = st.sidebar.selectbox("Escolha o Cérebro (Modelo):", 
                              ["mistralai/Mistral-7B-Instruct-v0.3", 
                               "meta-llama/Meta-Llama-3-8B-Instruct"])

# Instrução de Comportamento (Etapa 2 - Design do Agente)
instrucao = """Você é um Agente da Plataforma Atlas em Camaquã/RS. 
Seu objetivo é ajudar jovens a resolver problemas reais da comunidade 
usando inovação e ética, conforme as diretrizes da UNESCO."""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if prompt := st.chat_input("Como posso ajudar a comunidade hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamada segura para o Hugging Face usando Secrets
    if "HF_TOKEN" in st.secrets:
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        api_url = f"https://api-inference.huggingface.co/models/{modelo}"
        
    
           try:
            payload = {"inputs": f"{instrucao}\nUsuário: {prompt}\nAgente:", "parameters": {"max_new_tokens": 500}}
            response = requests.post(api_url, headers=headers, json=payload)
            response_json = response.json()
            
            if response.status_code == 200:
                full_text = response_json[0]['generated_text']
                resposta = full_text.split("Agente:")[-1].strip()
                with st.chat_message("assistant"):
                    st.markdown(resposta)
                    st.session_state.messages.append({"role": "assistant", "content": resposta})
            else:
                st.error(f"Erro da API ({response.status_code}): {response_json}")
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
        except:
            st.error("Erro ao acessar a IA. Verifique se o Token foi configurado no Streamlit Cloud.")
    else:
        st.warning("Aguardando configuração do Token de Acesso (Secrets).")
