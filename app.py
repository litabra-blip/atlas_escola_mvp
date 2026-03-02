import streamlit as st
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Atlas IA MVP", page_icon="🌍")

st.title("🚀 Plataforma Atlas - Camaquã")
st.subheader("Transformando jovens em criadores de IA")

# 2. Configurações na Sidebar
st.sidebar.header("Configurações")
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
        # NOVA URL DO ROUTER (CORREÇÃO DO ERRO 410)
        api_url = f"https://router.huggingface.co/hf-inference/models/{id_modelo}"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        
        # Instrução de sistema para o Agente Atlas
        instrucao = "Você é o Agente Atlas, um assistente educativo para alunos de Camaquã/RS. Responda em Português de forma prestativa."
        
        payload = {
            "inputs": f"{instrucao}\n\nUsuário: {prompt}\n\nAssistente:",
            "parameters": {"max_new_tokens": 500, "return_full_text": False}
        }

        try:
            with st.spinner("Conectando ao cérebro da IA..."):
                response = requests.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    res_json = response.json()
                    
                    # O Router costuma retornar uma lista com 'generated_text'
                    if isinstance(res_json, list) and len(res_json) > 0:
                        resposta = res_json[0].get('generated_text', 'Não consegui gerar uma resposta.')
                    elif isinstance(res_json, dict):
                        resposta = res_json.get('generated_text', 'Erro no formato da resposta.')
                    else:
                        resposta = "Resposta em formato desconhecido."

                    # Limpa a resposta de possíveis restos do prompt
                    resposta = resposta.replace("Assistente:", "").strip()

                    with st.chat_message("assistant"):
                        st.markdown(resposta)
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                
                elif response.status_code == 503:
                    st.warning("O modelo está sendo carregado. Tente novamente em alguns segundos.")
                else:
                    st.error(f"Erro {response.status_code}: {response.text}")
                    
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Configure o HF_TOKEN nos Secrets do Streamlit.")
