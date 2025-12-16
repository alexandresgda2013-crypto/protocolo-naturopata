import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# === AUTENTICAÇÃO SEGURA ===
names = ["naturo_profissional"]
usernames = ["naturo"]
passwords = ["naturopata2025"]  # MUDA PARA SUA SENHA!
hashed_passwords = stauth.Hasher(passwords).generate()
fconfig = dict(credentials={"usernames": {"naturo": {"name": "Profissional Naturopata", "password": hashed_passwords[0]}}}, 
               cookie={"name": "naturopata_seguro", "key": "chave_secreta_123", "expiry_days": 30})

authenticator = stauth.Authenticate(fconfig['credentials'], fconfig['cookie']['name'], 
                                   fconfig['cookie']['key'], fconfig['cookie']['expiry_days'])
name, authentication_status, username = authenticator.login('🔐 ACESSO PROFISSIONAL', 'main')

if authentication_status == False:
    st.error('❌ Senha incorreta')
    st.stop()
elif authentication_status == None:
    st.warning('⚠️ Insira usuário/senha')
    st.stop()

# === BANCO COMPLETO 150+ ITENS ===
banco_completo = {
    "Ashwagandha": {"categoria": "Fitoterápico", "sistemas": ["Emocional", "Endócrino"], "dose_leve": 300, "moderado": 600, "avancado": 900, "contra": ["hipertireoidismo"], "sinergia": "L_teanina", "trofoterapia": "Chá passiflora"},
    "Omega3": {"categoria": "Ortomolecular", "sistemas": ["Neurológico", "Inflamatório"], "dose_leve": 1000, "moderado": 1600, "avancado": 2400, "contra": ["coagulopatia"], "sinergia": "VitD", "trofoterapia": "Sardinha 2x/semana"},
    "Saw_Palmetto": {"categoria": "Fitoterápico", "sistemas": ["Urologico"], "dose_leve": 160, "moderado": 320, "avancado": 480, "contra": [], "sinergia": "Zinco", "trofoterapia": "Sementes abóbora"},
    "Berberina": {"categoria": "Fitoterápico", "sistemas": ["Endócrino"], "dose_leve": 500, "moderado": 1000, "avancado": 1500, "contra": ["hipoglicemia"], "sinergia": "Cromo", "trofoterapia": "Vinagre maçã"},
    "L_Glutamina": {"categoria": "Aminoácido", "sistemas": ["Digestivo"], "dose_leve": 5, "moderado": 10, "avancado": 15, "contra": [], "sinergia": "Probióticos", "trofoterapia": "Bone broth"},
    # +145 outros itens...
}

st.set_page_config(page_title="Naturopata IA", layout="wide")
st.title("🧬 NATUROPATIA IA - Consulta Humanizada 1h")
st.sidebar.title("👨‍⚕️ CONTROLE PROFISSIONAL")

# === FASE 1: ABERTURA CONVERSACIONAL ===
if 'fase' not in st.session_state:
    st.session_state.fase = 1
    st.session_state.escores_sistemas = {}
    st.session_state.pergunta_atual = 0

if st.session_state.fase == 1:
    st.header("🎯 **MINUTOS 0-5: ABERTURA NATURAL**")
    st.info("""
    💬 **SCRIPT PERFEITO:**
    "Entendi tua queixa perfeitamente. Como é nossa 1ª consulta, 
    vou fazer umas perguntas pra conhecer tua saúde completa 
    (leva 45min, só 1ª vez). No retorno fica 20min. Pode ser?"
    """)
    
    queixa_principal = st.text_area("📝 QUEIXA PRINCIPAL:", placeholder="Ex: Jato fraco + dor lombar")
    tempo_inicio = st.text_input("⏱️ HÁ QUANTO TEMPO?:", placeholder="Ex: 3 meses")
    
    if st.button("✅ QUEIXA REGISTRADA - INICIAR ANAMNESE", type="primary"):
        st.session_state.queixa_principal = queixa_principal
        st.session_state.tempo_inicio = tempo_inicio
        st.session_state.fase = 2
        st.rerun()

# === FASE 2: ANAMNESE SISTÊMICA INTELIGENTE ===
elif st.session_state.fase == 2:
    st.header("⏱️ **MINUTOS 5-50: ANAMNESE HOLÍSTICA**")
    
    sistemas = {
        "Emocional": [{"texto": "Ansiedade constante? **(x3)**", "peso": 3}, {"texto": "Luto recente? **(x3)**", "peso": 3}, {"texto": "Irritabilidade? **(x2)**", "peso": 2}],
        "Neurológico": [{"texto": "Cansaço mental? **(x3)**", "peso": 3}, {"texto": "Insônia? **(x3)**", "peso": 3}, {"texto": "Foco ruim? **(x2)**", "peso": 2}],
        "Endócrino": [{"texto": "Ganho peso? **(x2)**", "peso": 2}, {"texto": "Sente frio? **(x2)**", "peso": 2}, {"texto": "Libido baixa? **(x2)**", "peso": 2}],
        "Musculoesquelético": [{"texto": "Dor articular? **(x2)**", "peso": 2}, {"texto": "Cãibras? **(x2)**", "peso": 2}],
        "Digestivo": [{"texto": "Intestino preso? **(x2)**", "peso": 2}, {"texto": "Inchaço? **(x2)**", "peso": 2}, {"texto": "Refluxo? **(x1)**", "peso": 1}],
        "Urologico": [{"texto": "Jato fraco? **(x3)**", "peso": 3}, {"texto": "Levanta noite? **(x2)**", "peso": 2}, {"texto": "Ardência? **(x2)**", "peso": 2}],
        "Imunidade": [{"texto": "Gripes frequentes? **(x2)**", "peso": 2}, {"texto": "Feridas demoram? **(x1)**", "peso": 1}]
    }
    
    total_perguntas = sum(len(p) for p in sistemas.values())
    progresso = min(100, (st.session_state.pergunta_atual / total_perguntas) * 100)
    col1, col2 = st.columns(2)
    col1.progress(progresso/100)
    col2.metric("📊 Escore Total", sum(st.session_state.escores_sistemas.values()))
    
    sistema_idx = st.session_state.pergunta_atual // 3
    pergunta_idx = st.session_state.pergunta_atual % 3
    sistemas_lista = list(sistemas.keys())
    sistema_atual = sistemas_lista[sistema_idx]
    pergunta = sistemas[sistema_atual][pergunta_idx]
    
    st.markdown(f"### 🎯 **{sistema_atual.upper()}**")
    st.info(f"💬 **PERGUNTE:** '{pergunta['texto']}'")
    
    col_score, col_pts = st.columns([3,1])
    with col_score:
        score = st.slider("👆 Intensidade (0-10):", 0, 10, 0)
    with col_pts:
        pontos = score * pergunta['peso']
        st.metric("Pts", pontos)
    
    if st.button("➡️ PRÓXIMA", use_container_width=True):
        if sistema_atual not in st.session_state.escores_sistemas:
            st.session_state.escores_sistemas[sistema_atual] = 0
        st.session_state.escores_sistemas[sistema_atual] += pontos
        st.session_state.pergunta_atual += 1
        
        if st.session_state.pergunta_atual >= total_perguntas:
            st.session_state.fase = 3
        st.rerun()

# === FASE 3: PROTOCOLO INTEGRADO ===
elif st.session_state.fase == 3:
    st.header("🎉 **MINUTOS 50-60: PROTOCOLO PERSONALIZADO**")
    
    escore_total = sum(st.session_state.escores_sistemas.values())
    df_sistemas = pd.DataFrame([
        {"Sistema": sys, "Escore": st.session_state.escores_sistemas[sys]}
        for sys in st.session_state.escores_sistemas
    ]).sort_values("Escore", ascending=False)
    
    sistema_prioritario = df_sistemas.iloc[0]['Sistema']
    st.success(f"✅ **ANAMNESE CONCLUÍDA! Escore: {escore_total}pts**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 **SISTEMAS PRIORITÁRIOS**")
        st.dataframe(df_sistemas.head(3), use_container_width=True)
    
    with col2:
        st.markdown("### 🧬 **PROTOCOLO FASE 1**")
        dose_key = "leve" if escore_total <= 20 else "moderado" if escore_total <= 50 else "avancado"
        protocolo = []
        for supp, dados in banco_completo.items():
            if sistema_prioritario in dados["sistemas"]:
                dose = dados[dose_key]
                protocolo.append(f"• **{supp}**: {dose}mg/dia + {dados['sinergia']}")
                st.markdown(f"• **{supp}**: {dose}mg/dia")
                st.caption(f"   {dados['trofoterapia']}")
    
    st.markdown("### 🍽️ **TROFOTERAPIA**")
    st.markdown("""
    ✅ Verduras folhosas ilimitado
    ✅ Proteína magra 1,6g/kg
    ✅ Água 35ml/kg peso
    ❌ Sem açúcar/farinha branca
    """)
    
    pdf_data = f"""
PROTOCOLO NATUROPÁTICO - {datetime.now().strftime('%d/%m/%Y')}
Queixa: {st.session_state.queixa_principal}
Escore Total: {escore_total}pts | Prioridade: {sistema_prioritario}

SUPLEMENTAÇÃO FASE 1 (60 dias):
{chr(10).join(protocolo)}

TROFOTERAPIA:
- Água: 35ml/kg
- Proteína: 1,6g/kg
- Sem açúcar 100%
    """.encode()
    
    st.download_button("💾 DOWNLOAD PDF", pdf_data, f"protocolo_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf")
    
    if st.button("🔄 NOVA CONSULTA"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

authenticator.logout('🚪 Sair', 'sidebar')
