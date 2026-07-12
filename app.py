import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf

# 1. Configuration de la page Streamlit
st.set_page_config(
    page_title="Chaabi Assistant (TEST) - Banque Populaire", 
    page_icon="🏦", 
    layout="centered"
)

# Style CSS personnalisé (Couleurs de la Banque Populaire)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #E76F51; } /* Orange */
    .stButton>button { background-color: #1D3557; color: white; border-radius: 8px; } /* Bleu */
    </style>
""", unsafe_allow_html=True)

st.title("🏦 Chaabi Assistant AI (PROTOTYPE)")
st.subheader("Environnement de test - Banque Populaire Fictive")

# 2. Vérification et Connexion à l'API Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Clé API introuvable. Veuillez ajouter 'GEMINI_API_KEY' dans les Secrets de Streamlit.")
    st.stop()

# 3. Fausses métadonnées d'exemple pour le test (intégrées au prompt pour compatibilité)
SYSTEM_INSTRUCTION = """
Tu es 'Chaabi Assistant', un chatbot de démonstration pour une version fictive de la Banque Populaire du Maroc.
Tu devez utiliser UNIQUEMENT ces fausses métadonnées d'exemple si on te pose des questions institutionnelles :
- Nom officiel de simulation : Banque Populaire Fictionnelle (BPF)
- Siège social fictif : 404, Avenue de l'Intelligence Artificielle, Quartier Cyber-Tech, Casablanca.
- Numéro de Registre du Commerce (Faux) : RC Casa n° 999999-X
- Téléphone de test : +212 (0) 5 00 00 00 00
- Email fictif : contact@chaabi-assistant-test.ma

Aide l'utilisateur à simuler des demandes de cartes (La Blonde, Privilège), des comptes ou des crédits.
Sois toujours courtois, professionnel et réponds en français ou en arabe selon la langue de l'utilisateur.
"""

# 4. Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis votre conseiller virtuel de test. Comment puis-je vous aider aujourd'hui ?"}
    ]

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Barre latérale : Analyse de Documents
st.sidebar.header("📁 Analyse Documentaire")
uploaded_file = st.sidebar.file_uploader("Déposez un fichier (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])

document_context = ""

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        try:
            pdf_reader = pypdf.PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in pdf_reader.pages])
            document_context = f"\n[Contenu du PDF fourni] :\n{text[:3000]}"
            st.sidebar.success("✅ Fichier PDF lu !")
        except:
            st.sidebar.error("Erreur PDF.")
    else:
        try:
            image = Image.open(uploaded_file)
            st.sidebar.image(image, use_container_width=True)
            document_context = "\n[Le client a joint une image pour analyse.]"
            st.sidebar.success("✅ Image chargée !")
        except:
            st.sidebar.error("Erreur Image.")

# 6. Traitement du chat
if user_input := st.chat_input("Posez votre question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # MODIFICATION : Utilisation de gemini-pro pour éviter l'erreur 404 sur votre version de bibliothèque
            model = genai.GenerativeModel(model_name="gemini-pro")
            
            # Injection des instructions directement dans le prompt final pour assurer la compatibilité maximale
            prompt_final = f"{SYSTEM_INSTRUCTION}\n\nContexte actuel de la discussion :\n"
            if document_context:
                prompt_final += f"{document_context}\n"
            prompt_final += f"Message de l'utilisateur : {user_input}"
            
            response = model.generate_content(prompt_final)
            reponse_ia = response.text
            message_placeholder.markdown(reponse_ia)
            st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
        except Exception as e:
            st.error(f"Erreur : {e}")
            
