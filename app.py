import streamlit as st
import os
import pandas as pd


import json   #importation pour tab5
import plotly.express as px
import plotly.graph_objects as go
import base64
from dotenv import load_dotenv, find_dotenv
import openai
from github import Github
from pinecone import Pinecone

# Set up Streamlit page
st.set_page_config(
    page_title="VoxPopuli",
    page_icon="🌱",
    layout="wide",
)

# CSS pour le style
st.markdown(
    """
    <style>
    body {
        background-color: white;
    }
    .navbar {
        background-color: #FFFFFF;
        padding: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #F0F2F6;
        color: #31333F;
        font-weight: bold;
        font-size: 18px;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .navbar a {
        text-decoration: none;
        color: #31333F;
        margin: 0 15px;
    }
    .navbar a:hover {
        color: #FF4B4B;
    }
    .header {
        font-size: 28px;
        font-weight: bold;
        color: #FF4B4B;
        margin-bottom: 20px;
    }
    .card {
        background-color: #F9F9F9;
        padding: 20px;
        border-radius: 10px;
        margin: 50px 0;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
    }
    .card-title {
        font-size: 20px;
        font-weight: bold;
        color: #333;
    }
    .card-text {
        font-size: 16px;
        color: #666;
    }
    .comment {
        background-color: #f0f2f5;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 80%;
    }
    .comment-section {
        max-height: 150px;
        overflow-y: auto;
        padding-right: 10px;
    }
    .comment-box {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .comment-box input[type='text'] {
        flex: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    .comment-box button {
        background-color: #FF4B4B;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 12px;
        cursor: pointer;
    }
    .comment-box button:hover {
        background-color: #e43e3e;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"
if "comments" not in st.session_state:
    st.session_state["comments"] = [[] for _ in range(3)]
if "new_comments" not in st.session_state:
    st.session_state["new_comments"] = ["" for _ in range(3)]
if "proposals" not in st.session_state:
    st.session_state["proposals"] = []
if "announcements" not in st.session_state:
    st.session_state["announcements"] = [
        {
            "title": "Projet environnemental Rue de la Paix",
            "date": "10 février",
            "desc": "Une initiative pour réduire les déchets et promouvoir la biodiversité urbaine.",
            "image": "images/environment.jpg",
        },
        {
            "title": "Aménagement cyclable Avenue des Fleurs",
            "date": "15 février",
            "desc": "Proposition de nouvelles pistes cyclables pour une mobilité durable.",
            "image": "images/cycling.jpg",
        },
        {
            "title": "Réhabilitation de l'École Jean Moulin",
            "date": "20 février",
            "desc": "Travaux pour moderniser l'école et améliorer son efficacité énergétique.",
            "image": "images/school.jpg",
        },
    ]
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Admin Authentication with a Secret Code
def authenticate_admin(secret_code):
    if secret_code == "SECRET123":
        st.session_state["is_admin"] = True
        st.success("Access granted! You are now logged in as an admin.")
    else:
        st.error("Invalid secret code. Please try again.")

# Admin Authentication Section
if not st.session_state["is_admin"]:
    st.sidebar.subheader("Admin Login")
    admin_code = st.sidebar.text_input("Enter Admin Secret Code", type="password")
    if st.sidebar.button("Authenticate"):
        authenticate_admin(admin_code)

# Function to add a new announcement
def add_announcement(title, description, image_path):
    new_announcement = {
        "title": title,
        "date": "Ajoutée aujourd'hui",
        "desc": description,
        "image": image_path,
    }
    st.session_state["announcements"].append(new_announcement)
    st.session_state["comments"].append([])
    st.session_state["new_comments"].append("")

# Function to add an announcement to proposals
def add_to_proposals(index):
    announcement = st.session_state["announcements"][index]
    comments = st.session_state["comments"][index]
    st.session_state["proposals"].append({
        "announcement": announcement,
        "comments": comments.copy()
    })

# Gestion des pages
if st.session_state["current_page"] == "dashboard":
    st.button("⬅️ Retour aux analyses", on_click=lambda: st.session_state.update({"current_page": "home"}))
    st.markdown("<div class='header'>📈 Analyse du thème</div>", unsafe_allow_html=True)
    st.write("Voici les analyses détaillées pour le thème sélectionné.")

    # Exemple de tableau de bord
    st.subheader("Statistiques clés")
    st.bar_chart({"Mois": ["Janvier", "Février", "Mars"], "Réponses": [100, 150, 120]})
    st.subheader("Détails des réponses")
    st.dataframe(
        pd.DataFrame({
            "Catégorie": ["Très satisfait", "Satisfait", "Neutre", "Insatisfait", "Très insatisfait"],
            "Nombre": [40, 60, 30, 20, 10],
        })
    )
else:
    # Layout management
    if st.session_state["is_admin"]:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📢 Annonces", "📊 Sondages", "📊 Analyses", "💬 Chat", "📌 Propositions"])
    else:
        tab1, tab2, tab4, tab5 = st.tabs(["📢 Annonces", "📊 Sondages","💬 Chat", "📌 Propositions"])

    # Tab 1: Annonces
    with tab1:
        st.markdown("<div class='header'>📢 Annonces</div>", unsafe_allow_html=True)

        # Add new announcement
        with st.expander("Ajouter une nouvelle idée"):
            new_title = st.text_input("Titre de l'idée", key="new_title")
            new_desc = st.text_area("Description de l'idée", key="new_desc")
            new_image = st.file_uploader("Uploader une image", type=["png", "jpg", "jpeg"], key="new_image")
            if st.button("Soumettre", key="submit_new_idea"):
                if new_title and new_desc:
                    image_folder = "images"
                    if not os.path.exists(image_folder):
                        os.makedirs(image_folder)
                    image_path = "images/default.jpg"
                    if new_image:
                        image_path = os.path.join(image_folder, new_image.name)
                        with open(image_path, "wb") as f:
                            f.write(new_image.read())
                    add_announcement(new_title, new_desc, image_path)
                    st.success("Votre idée a été ajoutée avec succès !")
                else:
                    st.error("Veuillez remplir tous les champs.")

        # Display announcements
        for i, announcement in enumerate(st.session_state["announcements"]):
            if os.path.exists(announcement["image"]):
                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    st.image(announcement["image"], use_container_width=True)
                with col2:
                    st.markdown(
                        f"""
                        <div class="card-title">{announcement['title']}</div>
                        <div class="card-text">
                            <strong>{announcement['date']}</strong> - {announcement['desc']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col3:
                    # Restrict "Ajouter à Propositions" button to admin
                    if st.session_state["is_admin"]:
                        if st.button("Ajouter à Propositions", key=f"proposal_{i}"):
                            add_to_proposals(i)
                            st.success("Annonce ajoutée aux propositions !")

                # Comments section
                st.markdown("**Commentaires**")
                with st.container():
                    st.markdown(
                        f"<div class='comment-section'>" +
                        "".join([f"<div class='comment'>{comment}</div>" for comment in st.session_state['comments'][i]]) +
                        "</div>",
                        unsafe_allow_html=True,
                    )

                # Input and send button for comments
                comment_col1, comment_col2 = st.columns([8, 1])
                with comment_col1:
                    st.session_state["new_comments"][i] = st.text_input(
                        "Ajouter un commentaire", 
                        value=st.session_state["new_comments"][i], 
                        key=f"comment_input_{i}", 
                        label_visibility="collapsed"
                    )
                with comment_col2:
                    if st.button("➤", key=f"send_comment_{i}"):
                        if st.session_state["new_comments"][i].strip():
                            st.session_state["comments"][i].append(st.session_state["new_comments"][i].strip())
                            st.session_state["new_comments"][i] = ""

            else:
                st.error(f"Image non trouvée : {announcement['image']}")

    # Onglet 2 : Sondages
        with tab2:
            st.markdown("<div class='header'>📊 Sondages</div>", unsafe_allow_html=True)
            themes = ["Pollution environnementale", "Social", "Économie", "Transport", "Culture"]
            theme_selection = st.selectbox("Choisissez un thème :", themes)
            st.multiselect("Quels sont les sous-thèmes qui vous concernent le plus ?", [
                "Qualité de l'air",
                "Gestion des déchets",
                "Chauffage urbain",
                "Énergies renouvelables",
            ])
            st.text_area("Commentaires libres :", placeholder="Partagez vos idées...")
            if st.button("Soumettre"):
                st.success("Merci pour votre contribution !")
        
        # Onglet 3 : Analyses
        if st.session_state["is_admin"]:
            with tab3:
                st.markdown("<div class='header'>📈 Analyses</div>", unsafe_allow_html=True)

                analysis_themes = ["Pollution environnementale", "Social", "Économie", "Transport", "Culture"]
                st.markdown("### Cliquez sur un thème pour voir les analyses :")
                for theme in analysis_themes:
                    if st.button(f"📊 {theme}", key=theme):
                        st.session_state["current_page"] = "dashboard"

        # Onglet 4 : Chat
        with tab4:
            st.markdown("<div class='header'>💬 Chat</div>", unsafe_allow_html=True)
            chat_themes = ["Tous les thèmes", "Pollution environnementale", "Social", "Économie", "Transport", "Culture"]
            selected_chat_theme = st.selectbox("Choisissez un thème pour discuter :", chat_themes)

            st.text_area("Chatbot :", value="Bonjour ! Comment puis-je vous aider ?", height=200, key="chatbot_output", disabled=True)
            user_input = st.text_input("Vous :", placeholder="Tapez votre message ici...")

            if st.button("Envoyer"):
                if user_input:
                    # Ajoutez ici la logique pour traiter les messages avec un chatbot
                    chatbot_response = f"Vous avez choisi le thème '{selected_chat_theme}'. Voici une réponse automatique : {user_input}"
                    st.session_state.chatbot_output = chatbot_response
                else:
                    st.warning("Veuillez entrer un message avant d'envoyer.")

    # Tab 5: Propositions
    with tab5:
        st.markdown("<div class='header'>💬 Chat </div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='header' style='font-size: small; font-style: italic;'>"
            "IA entraînées sur le cours de M. Quentin CARDI, avec son autorisation, tous droits réservés"
            "</div>",
            unsafe_allow_html=True
        )

        def load_environment_variables(env_paths):
            """Load environment variables from specified paths."""
            for folder, filename in env_paths:
                dotenv_path = find_dotenv(os.path.join(folder, filename), raise_error_if_not_found=True, usecwd=True)
                load_dotenv(dotenv_path, override=True)

        def generate_openai_response(system_prompt, user_prompt, model_params, env_variables):
            """Generate a response from the OpenAI model."""
            openai.api_key = env_variables["openai_api_key"]

            try:
                response = openai.chat.completions.create(
                    model=model_params['selected_model'],
                    max_tokens=model_params['max_length'],
                    temperature=model_params['temperature'],
                    top_p=model_params['top_p'],
                    frequency_penalty=model_params['frequency_penalty'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.choices[0].message.content if response.choices else "No response found."
            except Exception as e:
                return f"An error occurred: {str(e)}"

        def get_embedding(text, model="text-embedding-3-small"):
            """Get text embedding."""
            response =  openai.embeddings.create(
                model=model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding

        def summarize_text(text, model="gpt-4o", max_length=512):
            """Summarize the given text."""
            try:
                response = openai.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": f"Summarize the following text:\n\n{text}"}],
                    max_tokens=max_length,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Summary error: {str(e)}"

        def refine_response(text, prompt, model="gpt-4o", max_length=1024):
            """Refine the response based on the prompt."""
            try:
                response = openai.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Tu adoptes le ton d'un assistant amical. Ton rôle est de parler de la participation citoyenne à l'aide des conaissances fournies"},
                        {"role": "user", "content": f"Affine et fait un sommaire des informations pertinentes afin de répondre à cette question : {prompt}\n\n{text}"}
                    ],
                    max_tokens=max_length,
                    temperature=1
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Refinement error: {str(e)}"

        # def extract_text_from_pdf(file_content):
        #     """Extract text from a PDF file."""
        #     images = convert_from_bytes(file_content, poppler_path=r'./myenv/poppler-24.08.0/Library/bin')
        #     pytesseract.pytesseract.tesseract_cmd = r"./myenv/Tesseract-OCR/tesseract.exe"
        #     text = "".join(pytesseract.image_to_string(image) for image in images)
        #     return text

        def chunk_text(text, max_tokens=8191):
            """Chunk text into manageable pieces."""
            words = text.split()
            chunks, current_chunk, current_length = [], [], 0

            for word in words:
                word_length = len(word) + 1  # Account for space
                if current_length + word_length <= max_tokens:
                    current_chunk.append(word)
                    current_length += word_length
                else:
                    chunks.append(" ".join(current_chunk))
                    current_chunk, current_length = [word], word_length

            if current_chunk:
                chunks.append(" ".join(current_chunk))

            return chunks

        # def process_and_store_documents(repo_docs, pinecone_instance):
        #     """Process documents and store them in Pinecone."""
        #     vectors = []
        #     progress_bar = st.progress(0)

        #     for doc_id, document in enumerate(repo_docs):
        #         extracted_text = extract_text_from_pdf(document['file_content'])
        #         text_chunks = chunk_text(extracted_text, max_tokens=8191)

        #         for i, chunk in enumerate(text_chunks):
        #             summary = summarize_text(chunk)
        #             vector = get_embedding(chunk)
        #             vectors.append({
        #                 "id": f"{doc_id}_{i}",
        #                 "values": vector,
        #                 "metadata": {
        #                     "file_path": document['file_path'],
        #                     "summary": summary
        #                 }
        #             })

        #         progress_bar.progress((doc_id + 1) / len(repo_docs))

        #     store_vectors_in_pinecone(pinecone_instance, vectors)

        def retrieve_github_documents(github_token, repo_name, branch='documents', path=None):
            """Retrieve documents from a GitHub repository."""
            g = Github(github_token)
            repo = g.get_repo(repo_name)
            contents = repo.get_contents(path or "", ref=branch)
            documents = []

            while contents:
                file_content = contents.pop(0)
                if file_content.type == 'file' and file_content.path.endswith('.pdf'):
                    content_file = repo.get_contents(file_content.path, ref=branch)
                    file_content_data = base64.b64decode(content_file.content)
                    documents.append({"file_path": file_content.path, "file_content": file_content_data})
                elif file_content.type == 'dir':
                    contents.extend(repo.get_contents(file_content.path, ref=branch))

            return documents

        def initialize_pinecone(api_key, index_name):
            """Initialize a Pinecone instance."""
            pc = Pinecone(api_key=api_key)
            index = pc.Index(index_name)
            return index

        def is_pinecone_index_empty(index):
            """Check if a Pinecone index is empty."""
            response = index.describe_index_stats()
            return response['namespaces']['ns1']['vector_count'] == 0

        def store_vectors_in_pinecone(index, vectors):
            """Store vectors in the Pinecone index."""
            index.upsert(vectors=vectors, namespace="ns1")

        def query_pinecone_index(index, query_vector, top_k=3):
            """Query the Pinecone index."""
            response = index.query(
                namespace="ns1",
                vector=query_vector,
                top_k=top_k,
                include_values=False,
                include_metadata=True
            )
            return response['matches']

        # Load environment variables
        #load_environment_variables([['env', '.env']]) directement inclu avec streamlit cloud

        env_variables = {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'pinecone_key': os.getenv('PINECONE_API_KEY'),
            'pinecone_index': os.getenv('PINECONE_INDEX_NAME'),
            'github_token': os.getenv('GITHUB_TOKEN'),
            'github_repo': os.getenv('GITHUB_REPO'),
            'github_branch': os.getenv('GITHUB_BRANCH', 'documents')
        }

        # Initialize Pinecone
        pinecone_index = initialize_pinecone(env_variables['pinecone_key'], env_variables['pinecone_index'])

# Verify if Pinecone index is initialized
# st.info notifications and process initialization if needed

# Clear UI
st.empty()

# Sidebar Configuration
with st.sidebar:
    with st.expander("Parameters"):
        selected_model = st.selectbox('Model', ['gpt-4o', 'o1-mini', 'gpt-3.5-turbo'], key='selected_model')
        temperature = st.slider('Creativity -/+:', min_value=0.01, max_value=1.0, value=0.8, step=0.01)
        top_p = st.slider('Words randomness -/+:', min_value=0.01, max_value=1.0, value=0.95, step=0.01)
        freq_penalty = st.slider('Frequency Penalty -/+:', min_value=-1.99, max_value=1.99, value=0.0, step=0.01)
        max_length = st.slider('Max Length', min_value=256, max_value=8192, value=4224, step=2)

    st.button('Clear Chat History', on_click=lambda: st.session_state.update({'messages': [{"role": "assistant", "content": "Posez vos questions relatives à la participation citoyenne et aux sciences politiques !"}]}))

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Posez vos questions relatives à la participation citoyenne et aux sciences politiques !"}]

# Use a container for chat messages
with st.container():
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.write(message.get("content", ""))

# Chat input handling stays out of the container
user_input = st.chat_input(placeholder="Qu'est-ce que la participation citoyenne ?")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    model_params = {
        'selected_model': selected_model,
        'temperature': temperature,
        'top_p': top_p,
        'frequency_penalty': freq_penalty,
        'max_length': max_length
    }
    # Chat input handling
    if user_input := st.chat_input(placeholder="Enter your message"):
        # Record user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.write(f"**User:** {user_input}")
    
        with st.spinner("Thinking . . . "):
            # Get the embedding for the user prompt
            query_vector = get_embedding(user_input)
            
            # Query the Pinecone index
            results = query_pinecone_index(pinecone_index, query_vector)
            
            # Compile summaries from queried results
            all_summaries = "\n".join([
                f"File: {item.metadata['file_path']} - Summary: {item.metadata['summary']} - Score: {item['score']}"
                for item in results if item.metadata
            ]) if results else "No relevant information found."
            
            # Refine the response based on available summaries
            refined_response = refine_response(all_summaries, user_input)
            
            # Display the assistant's response
            st.write(f"**Assistant:** {refined_response}")
    
        # Append assistant's response to chat history
        st.session_state.messages.append({"role": "assistant", "content": refined_response})
