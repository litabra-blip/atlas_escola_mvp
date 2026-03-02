import streamlit as st
import requests

st.set_page_config(page_title="Atlas IA", page_icon="🌍")
st.title("🚀 Plataforma Atlas - Camaquã")

# Modelo com maior taxa de sucesso em tokens gratuitos
id_modelo = "mistralai/Mistral-7B-Instruct-v0.2"

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
        # TENTATIVA DIRETA (Muitas vezes o Router causa 404 se o token for muito recente)
        api_url = f"https://api-inference.huggingface.co/models/{id_modelo}"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN'].strip()}"}
        
        payload = {
            "inputs": f"<s>[INST] Responda em Português: {prompt} [/INST]",
            "parameters": {"max_new_tokens": 500, "wait_for_model": True}
        }

        try:
            with st.spinner("Conectando ao Atlas..."):
                response = requests.post(api_url, headers=headers, json=payload)
                
                # Se a URL direta der erro 410, ele pula para o Router
                if response.status_code == 410:
                    api_url = f"https://router.huggingface.co/hf-inference/models/{id_modelo}"
                    response = requests.post(api_url, headers=headers, json=payload)

                if response.status_code == 200:
                    res_json = response.json()
                    output = res_json[0].get('generated_text', '') if isinstance(res_json, list) else res_json.get('generated_text', '')
                    resposta = output.split("[/INST]")[-1].strip()
                    
                    with st.chat_message("assistant"):
                        st.markdown(resposta)
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                else:
                    # Mensagem de diagnóstico real
                    st.error(f"Erro {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
