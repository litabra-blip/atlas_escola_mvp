import streamlit as st
import requests

st.set_page_config(page_title="Atlas IA", page_icon="🌍")

st.title("🚀 Plataforma Atlas - Camaquã")
st.markdown("---")

# Modelo de alta disponibilidade
id_modelo = "mistralai/Mistral-7B-Instruct-v0.2"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Olá! Eu sou o Atlas. Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "HF_TOKEN" in st.secrets:
        # Usando o endpoint de roteamento oficial (Router)
        api_url = f"https://router.huggingface.co/hf-inference/models/{id_modelo}"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        payload = {
            "inputs": f"<s>[INST] Você é o Agente Atlas, uma IA focada em educação e inovação em Camaquã/RS. Responda em Português: {prompt} [/INST]",
            "parameters": {"max_new_tokens": 500, "wait_for_model": True}
        }

        try:
            with st.spinner("Atlas está processando sua ideia..."):
                response = requests.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    res_json = response.json()
                    output = res_json[0].get('generated_text', '') if isinstance(res_json, list) else res_json.get('generated_text', '')
                    resposta = output.split("[/INST]")[-1].strip()
                    
                    with st.chat_message("assistant"):
                        st.markdown(resposta)
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                else:
                    st.error(f"Erro {response.status_code}. Verifique o segredo HF_TOKEN.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Configuração pendente: Adicione o HF_TOKEN nos Secrets do Streamlit.")
