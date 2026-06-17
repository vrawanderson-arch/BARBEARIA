import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai

# Importações dos novos módulos
from dashboard_charts import create_advanced_dashboard
from google_service import GoogleService

# Configuração da página
st.set_page_config(
    page_title="Agente IA Salão de Beleza Pro",
    page_icon="✂️",
    layout="wide"
)

# Tenta carregar .env localmente, mas prioriza st.secrets no Cloud
load_dotenv()

def get_secret(key, default=None):
    """Recupera segredos do st.secrets ou variáveis de ambiente"""
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

# Configurações globais
SALAO_INFO = {
    'nome': get_secret("SALAO_NOME", "Salão Bella"),
    'endereco': get_secret("SALAO_ENDERECO", "Rua das Flores, 123"),
    'telefone': get_secret("SALAO_TELEFONE", "(81) 99999-9999"),
    'ia_nome': get_secret("IA_NOME", "Sofia")
}

GEMINI_KEY = get_secret("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# Lógica para Google Credentials no Streamlit Cloud
# No Cloud, colamos o conteúdo do credentials.json no st.secrets["GOOGLE_CREDENTIALS_JSON"]
if 'google_service' not in st.session_state:
    try:
        if get_secret("GOOGLE_TOKEN_JSON"):
            st.session_state.google_service = GoogleService()
        else:
            st.session_state.google_service = None

    except Exception as e:
        st.session_state.google_service = None
        st.sidebar.warning(f"Google Service: {e}")

# Inicializar Agendamentos
if 'agendamentos' not in st.session_state:
    st.session_state.agendamentos = [
        {'id': 1, 'cliente': 'Ana Souza', 'servico': 'Manicure', 'data': '2026-06-20 14:00', 'status': 'Confirmado', 'telefone': '(81) 98765-4321', 'email': 'ana@email.com'},
        {'id': 2, 'cliente': 'Pedro Silva', 'servico': 'Corte masculino', 'data': '2026-06-21 09:30', 'status': 'Confirmado', 'telefone': '(81) 99876-5432', 'email': 'pedro@email.com'}
    ]

# --- UI STREAMLIT ---
st.sidebar.title(f"✂️ {SALAO_INFO['nome']}")
menu = st.sidebar.radio("Navegação", ["📊 Dashboard Avançado", "📅 Agendamentos", "💬 Chat IA", "⚙️ Integrações"])

if menu == "📊 Dashboard Avançado":
    st.header("📊 Dashboard de Performance")
    df = pd.DataFrame(st.session_state.agendamentos)
    
    col1, col2, col3 = st.columns(3)
    fig_status, fig_receita, fig_evolucao = create_advanced_dashboard(df)
    
    if fig_status:
        with col1: st.plotly_chart(fig_status, use_container_width=True)
        with col2: st.plotly_chart(fig_receita, use_container_width=True)
        with col3: st.plotly_chart(fig_evolucao, use_container_width=True)
    else:
        st.info("Sem dados suficientes para gerar o dashboard.")

elif menu == "📅 Agendamentos":
    st.header("📅 Gerenciar Agendamentos")
    
    with st.expander("➕ Novo Agendamento"):
        with st.form("novo_agendamento"):
            nome = st.text_input("Nome do Cliente")
            email = st.text_input("E-mail (para notificação)")
            servico = st.selectbox("Serviço", ["Corte feminino", "Corte masculino", "Manicure", "Pedicure", "Coloração"])
            data = st.date_input("Data")
            hora = st.time_input("Hora")
            submit = st.form_submit_button("Agendar")
            
            if submit:
                data_hora = f"{data} {hora}"
                novo = {'id': len(st.session_state.agendamentos)+1, 'cliente': nome, 'servico': servico, 'data': data_hora, 'status': 'Confirmado', 'email': email}
                st.session_state.agendamentos.append(novo)
                
                # Integração Google Calendar
                if st.session_state.google_service:
                    try:
                        start = f"{data}T{hora}:00"
                        end = (datetime.combine(data, hora) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
                        link = st.session_state.google_service.add_event(f"{servico} - {nome}", start, end)
                        if link: st.success(f"Adicionado ao Google Calendar! [Ver evento]({link})")
                    except: st.error("Erro ao conectar com Google Calendar.")
                
                # Integração Gmail
                if st.session_state.google_service and email:
                    try:
                        st.session_state.google_service.send_email(
                            email, 
                            f"Confirmação de Agendamento - {SALAO_INFO['nome']}",
                            f"Olá {nome}, seu agendamento de {servico} está confirmado para {data_hora}."
                        )
                        st.success("E-mail de confirmação enviado!")
                    except: st.error("Erro ao enviar e-mail.")
                
                st.rerun()

    st.table(pd.DataFrame(st.session_state.agendamentos))

elif menu == "💬 Chat IA":
    st.header(f"💬 Conversar com {SALAO_INFO['ia_nome']}")
    user_input = st.chat_input("Como posso ajudar?")
    if user_input:
        st.write(f"👤 Você: {user_input}")
        if GEMINI_KEY:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(user_input)
            st.write(f"💬 {SALAO_INFO['ia_nome']}: {response.text}")
        else:
            st.error("Gemini API Key não configurada nos Secrets.")

elif menu == "⚙️ Integrações":
    st.header("⚙️ Status das Integrações")
    
    st.info("💡 No Streamlit Cloud, use a aba 'Secrets' nas configurações do App para inserir suas chaves.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🤖 Telegram Bot")
        if get_secret("TELEGRAM_BOT_TOKEN"):
            st.success("✅ Token Configurado")
            st.code("python integrations/telegram_bot.py", language="bash")
        else:
            st.error("❌ Token não encontrado")

    with col2:
        st.subheader("☁️ Google API")

    if get_secret("GOOGLE_SERVICE_ACCOUNT"):
        st.success("✅ Google Service Account configurado")

        if st.session_state.google_service:
            st.success("✅ Autenticado")
        else:
            st.warning("⚠️ Token encontrado mas não autenticado")
    else:
        st.error("❌ GOOGLE_SERVICE_ACCOUNT não configurado")
