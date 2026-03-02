import streamlit as st
import requests

st.set_page_config(page_title="Atlas IA MVP", page_icon="🌍")

st.title("🚀 Plataforma Atlas - Camaquã")
st.subheader("Transformando jovens em criadores de IA")

# Sidebar
st.sidebar.header("Configurações")
# Mistral v0.2 é o modelo mais estável para a API Gratuita (Serverless)
id_modelo = "mistralai/Mistral-7B-Instruct-v0.2"
st.sidebar.info(f"Modelo Ativo: {id_modelo}")

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
        # Usando a URL de inferência direta (mais compatível com tokens grátis)
        api_url = f"https://api-inference.huggingface.co/models/{id_modelo}"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        payload = {
            "inputs": f"<s>[INST] Você é o Agente Atlas de Camaquã/RS. Responda em Português: {prompt} [/INST]",
            "parameters": {"max_new_tokens": 500, "wait_for_model": True}
        }

        try:
            with st.spinner("Atlas está processando..."):
                response = requests.post(api_url, headers=headers, json=payload)
                
                # Se der 410 (o erro anterior), forçamos o Router manualmente aqui
                if response.status_code == 410:
                    api_url = f"https://router.huggingface.co/hf-inference/models/{id_modelo}"
                    response = requests.post(api_url, headers=headers, json=payload)

                if response.status_code == 200:
                    res_json = response.json()
                    output = res_json[0].get('generated_text', '') if isinstance(res_json, list) else res_json.get('generated_text', '')
                    # Limpa a resposta para mostrar só o que vem depois do [/INST]
                    resposta = output.split("[/INST]")[-1].strip()
                    
                    with st.chat_message("assistant"):
                        st.markdown(resposta)
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                
                elif response.status_code == 503:
                    st.warning("O modelo está sendo preparado. Aguarde 30 segundos e tente enviar novamente.")
                else:
                    st.error(f"Status {response.status_code}: {response.text}")
                    
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Erro: HF_TOKEN não encontrado nos Secrets do Streamlit.")
        
