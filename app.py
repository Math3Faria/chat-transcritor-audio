import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment 
import os
from dotenv import load_dotenv
import google.generativeai as genai 

# --- Configurações Iniciais ---
load_dotenv()

st.set_page_config(page_title="Transcrição e Tradução de Áudio", layout="wide")

# --- CSS para o GIF de Fundo e Estilização Geral ---
st.markdown(
    """
    <style>
    /* GIF Background */
    .stApp {
        background-image: url("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHFheHB0bmtmZHdsMXM2OGFuZnR2cTc4bmxxdmEwY3Bic3gyZjd5ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/h4HHnU9RXd1Dvc24Gs/giphy.gif"); /* Seu GIF URL */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed; /* Mantém o GIF estático ao rolar */
    }

    /* Main Container Styling - Mais transparente! */
    .main .block-container {
        padding-top: 2rem;
        padding-right: 1.5rem; /* Aumentado o padding lateral */
        padding-left: 1.5rem;  /* Aumentado o padding lateral */
        padding-bottom: 2rem;
        background-color: rgba(255, 255, 255, 0.4); /* Menos opaco, mais transparente */
        border-radius: 20px; /* Bordas mais arredondadas */
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2); /* Sombra mais pronunciada */
        max-width: 750px; /* Um pouco mais largo para melhor leitura */
        margin: auto; /* Centraliza o container */
        backdrop-filter: blur(5px); /* Efeito de desfoque para o conteúdo */
    }

    /* Title Styling */
    h1 {
        color: #1a1a1a; /* Quase preto para forte contraste */
        text-align: center;
        margin-bottom: 1.8rem; /* Mais espaçamento abaixo do título */
        font-size: 2.8em; /* Título maior e mais impactante */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Fonte mais moderna */
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1); /* Sombra sutil no texto */
    }

    /* Subheader Styling */
    h2, h3, h4, h5, h6 {
        color: #333333;
        margin-top: 2rem; /* Mais espaçamento acima dos sub-cabeçalhos */
        margin-bottom: 1.2rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Markdown text */
    p, .stMarkdown, label {
        color: #444444; /* Cor do texto um pouco mais escura para legibilidade */
        line-height: 1.7; /* Mais espaço entre as linhas */
        font-size: 1.05em; /* Texto um pouco maior */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(to right, #007bff, #00bcd4); /* Gradiente de azul para ciano */
        color: white;
        border-radius: 10px; /* Bordas mais arredondadas */
        padding: 0.8rem 1.8rem; /* Mais padding para o botão */
        font-size: 1.2em; /* Texto do botão maior */
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); /* Sombra mais suave */
        transition: all 0.3s ease; /* Transição para hover */
        cursor: pointer;
    }

    .stButton > button:hover {
        transform: translateY(-2px); /* Efeito de "levantar" no hover */
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3); /* Sombra mais intensa no hover */
        background: linear-gradient(to right, #0056b3, #008c9e); /* Gradiente mais escuro no hover */
    }

    /* File Uploader Styling */
    .stFileUploader label {
        color: #333333;
        font-weight: bold;
        font-size: 1.1em;
    }

    /* Selectbox Styling */
    .stSelectbox label {
        color: #333333;
        font-weight: bold;
        font-size: 1.1em;
    }

    /* Info, Warning, Error, Success Messages - Cores mais suaves */
    .stAlert {
        border-radius: 10px; /* Mais arredondado */
        padding: 1.2rem; /* Mais padding */
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
        font-size: 1.05em;
    }

    .stAlert.info {
        background-color: #e3f2fd; /* Azul mais claro */
        color: #2196f3; /* Azul primário */
        border-left: 6px solid #2196f3;
    }
    .stAlert.warning {
        background-color: #fff3e0; /* Laranja suave */
        color: #ff9800; /* Laranja primário */
        border-left: 6px solid #ff9800;
    }
    .stAlert.error {
        background-color: #ffebee; /* Vermelho claro */
        color: #f44336; /* Vermelho primário */
        border-left: 6px solid #f44336;
    }
    .stAlert.success {
        background-color: #e8f5e9; /* Verde claro */
        color: #4caf50; /* Verde primário */
        border-left: 6px solid #4caf50;
    }

    /* Horizontal Rule */
    hr {
        border-top: 1px solid #dddddd; /* Linha mais clara */
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
    }

    /* Footer Text */
    .stMarkdown small {
        color: #777777;
        text-align: center;
        display: block;
        margin-top: 2rem;
        font-size: 0.9em;
    }

    /* Adicional: Player de áudio mais discreto */
    audio {
        width: 100%;
        margin-top: 1rem;
        margin-bottom: 1rem;
        filter: invert(10%); /* Escurece um pouco o player para combinar */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Cabeçalho da Aplicação ---
st.title(" Transcritor e Tradutor de Áudio do Matheus🤯")
st.markdown("Transforme **áudios** em **texto** e traduza para **diversos idiomas** usando o poder da inteligência artificial!")

# --- Configuração da API Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)

        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)

        MODEL_NAME = None 

        preferred_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

        for p_model_suffix in preferred_models:
            if f'models/{p_model_suffix}' in available_models:
                MODEL_NAME = p_model_suffix
                break
            elif p_model_suffix in available_models:
                MODEL_NAME = p_model_suffix
                break
            elif f'models/{p_model_suffix}-latest' in available_models:
                MODEL_NAME = f'{p_model_suffix}-latest'
                break

        if MODEL_NAME:
            if "vision-latest" in MODEL_NAME and not any(p in MODEL_NAME for p in ['gemini-1.5-flash', 'gemini-1.5-pro']):
                st.warning(f"⚠️ O modelo `{MODEL_NAME}` foi selecionado, mas ele é uma versão 'vision' ou está sendo depreciado. "
                           "Para melhor performance e longevidade, procure por `gemini-1.5-flash` ou `gemini-1.5-pro` em sua região.")
            elif MODEL_NAME == 'gemini-pro':
                st.warning("⚠️ O modelo 'gemini-pro' está sendo usado, mas ele será depreciado em breve. "
                           "Considere mudar para `gemini-1.5-flash` ou `gemini-1.5-pro` para maior longevidade e recursos.")

            model = genai.GenerativeModel(MODEL_NAME)
            st.success(f"API Gemini configurada com sucesso. Usando o modelo: `{MODEL_NAME}`.")
        else:
            st.error("❌ Nenhum modelo da API Gemini com capacidade de 'generateContent' foi encontrado. "
                     "Verifique as permissões da sua API Key ou a disponibilidade dos modelos na sua região. "
                     "Modelos de texto preferidos não disponíveis: " + ", ".join(preferred_models))
            st.stop()

    except Exception as e:
        st.error(f"❌ Erro ao configurar a API Gemini. Verifique sua chave ou conexão: {e}")
        st.stop()
else:
    st.error("🔑 A chave da API Gemini não foi encontrada. Certifique-se de configurar a variável de ambiente `GEMINI_API_KEY` "
             "no seu arquivo `.env` (localmente) ou nas 'Secrets' (na nuvem).")
    st.stop()

# --- Barra Lateral para Configurações ---
st.sidebar.header("⚙️ Configurações")

st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Idioma de Destino")
languages = {
    "Português": "pt",
    "Inglês": "en",
    "Espanhol": "es",
    "Francês": "fr",
    "Alemão": "de",
    "Italiano": "it",
    "Japonês": "ja",
    "Chinês (Simplificado)": "zh-CN",
    "Hindi": "hi",
    "Russo": "ru",
    "Árabe": "ar"
}
target_language_name = st.sidebar.selectbox(
    "Selecione o idioma para a tradução:",
    list(languages.keys()),
    index=0 
)
target_language_code = languages[target_language_name]
st.sidebar.markdown("---")


# --- Área Principal de Upload ---
st.subheader("⬆️ Faça o Upload do seu Áudio")
uploaded_file = st.file_uploader("Selecione um arquivo de áudio WAV (Máx: 25MB para SpeechRecognition)", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")

    temp_wav_path = "temp_audio.wav"

    with open(temp_wav_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("✨ Processar Áudio"):
        with st.spinner("⏳ Processando áudio... A precisão da transcrição pode variar."):
            transcribed_text = ""
            translated_text = ""
            try:
                r = sr.Recognizer()
                with sr.AudioFile(temp_wav_path) as source:
                    r.adjust_for_ambient_noise(source) 
                    audio_listened = r.record(source)

                try:
                    transcribed_text = r.recognize_google(audio_listened, language="pt-BR")
                    st.subheader("📝 Transcrição Original:")
                    with st.expander("Ver Transcrição"):
                        st.success(transcribed_text)
                except sr.UnknownValueError:
                    st.warning("⚠️ Não foi possível entender o áudio. A transcrição pode estar vazia ou incorreta.")
                    transcribed_text = "NÃO FOI POSSÍVEL TRANSCREVER O ÁUDIO" 
                    with st.expander("Ver Transcrição"):
                        st.info(transcribed_text)
                except sr.RequestError as e:
                    st.error(f"❌ Erro no serviço de reconhecimento de fala; verifique sua conexão com a internet ou as configurações: {e}")
                    transcribed_text = "ERRO NA TRANSCRIÇÃO" 
                    with st.expander("Ver Transcrição"):
                        st.info(transcribed_text)

                if transcribed_text and GEMINI_API_KEY and \
                   transcribed_text not in ["NÃO FOI POSSÍVEL TRANSCREVER O ÁUDIO", "ERRO NA TRANSCRIÇÃO"]:
                    st.subheader(f"🌐 Tradução para {target_language_name}:")
                    try:
                        prompt = f"Traduza o seguinte texto para o idioma {target_language_name}:\n\n{transcribed_text}"
                        response = model.generate_content(prompt)
                        translated_text = response.text
                        with st.expander("Ver Tradução"):
                            st.success(translated_text)
                    except Exception as e:
                        st.error(f"❌ Erro ao traduzir o texto com a API Gemini: {e}")
                        translated_text = "ERRO NA TRADUÇÃO"
                        with st.expander("Ver Tradução"):
                            st.warning(translated_text)
                elif not transcribed_text or transcribed_text in ["NÃO FOI POSSÍVEL TRANSCREVER O ÁUDIO", "ERRO NA TRANSCRIÇÃO"]:
                    st.info("ℹ️ Não há texto válido para traduzir, pois a transcrição falhou.")
                else:
                    st.info("ℹ️ Tradução não realizada devido a problemas na transcrição ou falta da chave da API Gemini.")

            except Exception as e:
                st.error(f"🔥 Ocorreu um erro inesperado durante o processamento do áudio: {e}")
            finally:
                if os.path.exists(temp_wav_path):
                    os.remove(temp_wav_path)
else:
    st.info("👆 Por favor, faça upload de um arquivo WAV para começar a transcrever e traduzir.")

st.markdown("---")
st.markdown("Desenvolvido com o poder da **IA** para simplificar suas transcrições e traduções.")
st.markdown("Feito por **Matheus**")