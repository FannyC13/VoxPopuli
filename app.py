import streamlit as st
import os
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

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
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"

# Load comments from JSON file
comments_file = "data/comments.json"
if "comments" not in st.session_state:
    try:
        with open(comments_file, "r", encoding="utf-8") as f:
            st.session_state["comments"] = json.load(f)
    except FileNotFoundError:
        st.session_state["comments"] = [[] for _ in range(3)]

# Load proposals from JSON file
proposals_file = "data/pinned_ideas.json"
if "proposals" not in st.session_state:
    try:
        with open(proposals_file, "r", encoding="utf-8") as f:
            st.session_state["proposals"] = json.load(f)
    except FileNotFoundError:
        st.session_state["proposals"] = []

if "new_comments" not in st.session_state:
    st.session_state["new_comments"] = ["" for _ in range(len(st.session_state["comments"]))]
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
    st.session_state["proposals"].append(new_announcement)
    st.session_state["comments"].append([])
    st.session_state["new_comments"].append("")

# Function to add an announcement to proposals
def add_to_proposals(index):
    announcement = st.session_state["proposals"][index]
    comments = st.session_state["comments"][index]
    st.session_state["proposals"].append({
        "announcement": announcement,
        "comments": comments.copy()
    })

# Helper functions
def save_comments():
    with open(comments_file, "w", encoding="utf-8") as f:
        json.dump(st.session_state["comments"], f, indent=4, ensure_ascii=False)

def save_proposals():
    with open(proposals_file, "w", encoding="utf-8") as f:
        json.dump(st.session_state["proposals"], f, indent=4, ensure_ascii=False)

def display_propositions():
    for proposal in st.session_state["proposals"]:
        comments = [c["Comment"] for c in st.session_state["comments"] if c["Id_idea"] == proposal["ID"]]
        with st.container():
            # Colonnes pour l'image, contenu et boutons
            col_image, col_content, col_buttons = st.columns([1, 4, 1.5], gap="small")
            
            # Colonne pour l'image
            with col_image:
                st.image(proposal["Path image"], width=120)

            # Colonne pour le contenu
            with col_content:
                st.markdown(
                    f"""<h4 style='margin: 0; padding: 0;'>{proposal["Titre de l'idée"]}</h4>""",
                    unsafe_allow_html=True,
                )
                st.write(f"""<p style='margin: 0;'>{proposal["Description de l'idée"]}</p>""", unsafe_allow_html=True)
                st.write(f"**Fin du sondage**: {proposal['Fin du sondage']}")

            # Colonne pour les boutons "Like" et "Dislike"
            with col_buttons:
                col_like, col_dislike = st.columns([1, 1], gap="small")
                with col_like:
                    if st.button(f"👍 {proposal['Nb likes']}", key=f"like_{proposal['ID']}"):
                        proposal["Nb likes"] = str(int(proposal["Nb likes"]) + 1)
                        st.rerun()
                        save_proposals()
                      
                with col_dislike:
                    if st.button(f"👎 {proposal['Nb dislikes']}", key=f"dislike_{proposal['ID']}"):
                        proposal["Nb dislikes"] = str(int(proposal["Nb dislikes"]) + 1)
                        save_proposals()
                        st.rerun()

            # Section des commentaires
            st.markdown("<h5 style='margin-top: 30px; margin-bottom : 10px;'>💬 Commentaires</h5>", unsafe_allow_html=True)
            for comment in comments:
                st.markdown(f"{comment}")
                st.markdown("<hr style='margin: 1px 0; height: 1px; border: none; background-color: #D3D3D3;'>", unsafe_allow_html=True)

            # Champ de texte et bouton "Envoyer" alignés
            col_input, col_send = st.columns([8, 1], gap="small")
            with col_input:
                new_comment = st.text_input("", placeholder="Ajouter un commentaire", key=f"comment_{proposal['ID']}")
            with col_send:
                st.markdown(
                        """
                        <style>
                            .stButton button {
                                margin-top: 12px; 
                                
                            }
                        </style>
                        """,
                        unsafe_allow_html=True,
                )
                if st.button("➤", key=f"send_{proposal['ID']}"):
                    if new_comment.strip():
                        st.session_state["comments"].append({"Id_idea": proposal["ID"], "Comment": new_comment})
                        save_comments()
                        st.rerun()
                    else:
                        st.error("Veuillez entrer un commentaire valide.")
              
        
        st.markdown("---")  

  

def load_proposals(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except FileNotFoundError:
        st.error(f"Le fichier {file_path} est introuvable.")
        return pd.DataFrame()


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
    # ON VIRE SONDAGE (2) (useless étant donné notre process), ON VIRE ANNONCES (1) on garde que propositions (5) puisque c'est la même chose.
    if st.session_state["is_admin"]:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Propositions", "☝️ Ma proposition", "📊 Dashboard", "➕ Consulter","💬 Chat"])
    else:
        tab1, tab2, tab5 = st.tabs(["📌 Propositions","☝️ Ma proposition", "💬 Chat"])

    # Tab 1: Propositions
    with tab1:
        display_propositions()

    # Onglet 2 : Ma proposition
    with tab2:
        st.markdown("<div class='header'>☝️ Ma proposition</div>", unsafe_allow_html=True)

        # Grosse boîte de texte pour la proposition
        user_proposal = st.text_area("Veuillez entrer votre proposition :", placeholder="Écrivez votre proposition ici...", height=200)

        # Bouton pour soumettre la proposition
        if st.button("Envoyer ma proposition"):
            if user_proposal.strip():
                # Charger le fichier JSON existant
                proposals_file = "data/propositions_maille_verbatim.json"
                try:
                    with open(proposals_file, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                except FileNotFoundError:
                    existing_data = []

                # Ajouter la nouvelle proposition avec placeholders
                new_proposal = {
                    "Timestamp": pd.Timestamp.now().strftime("%d/%m/%Y"),
                    "Proposition": user_proposal.strip(),
                    "Catégorie": "a",
                    "Sous catégorie": "b",
                }
                existing_data.append(new_proposal)

                # Enregistrer les modifications dans le fichier JSON
                with open(proposals_file, "w", encoding="utf-8") as f:
                    json.dump(existing_data, f, indent=4, ensure_ascii=False)

                # Message de confirmation
                st.success("Merci pour votre proposition !")
            else:
                st.error("Veuillez entrer une proposition avant de soumettre.")


        
    # Onglet 3 : Dashboard
    if st.session_state["is_admin"]:
        with tab3:
            st.markdown("<div class='header'>📊 Dashboard</div>", unsafe_allow_html=True)
            # Charger les données JSON
            file_path = "data/propositions_maille_item.json"
            df = load_proposals(file_path)

            # Vérification si le dataframe est vide
            if not df.empty:
                # Menu déroulant pour choisir la catégorie
                selected_category = st.selectbox("Sélectionnez une catégorie :", sorted(df["Catégorie"].unique()))

                # Filtrer les données selon la catégorie sélectionnée
                filtered_df = df[df["Catégorie"] == selected_category]

                # Préparer les données pour le graphique
                sentiment_counts = (
                    filtered_df.groupby(["Sous catégorie", "Sentiment"])
                    .size()
                    .reset_index(name="Nombre de commentaires")
                )

                sentiment_counts["Nombre de commentaires"] = sentiment_counts.apply( lambda row: -row["Nombre de commentaires"] if row["Sentiment"] == "Négatif" else row["Nombre de commentaires"], axis=1 )

                # Créer un barchart personnalisé avec Plotly
                fig = go.Figure()

                # Couleurs personnalisées pour les sentiments
                sentiment_colors = {"Positif": "#2ecc71", "Négatif": "#e74c3c"}

                for sentiment in sentiment_counts["Sentiment"].unique():
                    data = sentiment_counts[sentiment_counts["Sentiment"] == sentiment]
                    fig.add_trace(
                        go.Bar(
                            x=data["Nombre de commentaires"],
                            y=data["Sous catégorie"],
                            name=sentiment,
                            orientation="h",
                            marker=dict(color=sentiment_colors[sentiment], line=dict(width=0.5, color="#333")),
                            width=0.3,  # Rendre les barres plus fines
                            hoverinfo="x+y+name"
                        )
                    )
                # Mettre à jour la mise en page pour plus d'esthétique
                fig.update_layout(
                title=f"Répartition des sentiments pour {selected_category}",
                xaxis=dict(
                    title="Nombre de commentaires",
                    zeroline=True,
                    zerolinecolor="#000",
                    showgrid=True,
                    gridcolor="#f0f0f0"
                ),
                yaxis=dict(
                    title="Sous catégorie",
                    categoryorder="total ascending"
                ),
                barmode="relative",  # Empilement centré sur 0
                height=600,
                margin=dict(l=100, r=40, t=70, b=50),
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(size=14, family="Arial"),
                legend=dict(title="Sentiments", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )

                # Ajuster l'apparence des axes
                fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0", zerolinecolor="#ccc")
                fig.update_yaxes(categoryorder="total ascending", showgrid=False)

                # Afficher le graphique
                st.plotly_chart(fig, use_container_width=True)
            
            else:                 
                st.warning("Aucune donnée disponible pour le moment.")

            # Template de rapport sur ce qui s'est dit dans les propositions (beaucoup de problèmes avec l'accessibilité des infos sur le web)
            st.markdown("""
            Ce mois-ci, nous avons reçu un total de **30** propositions. Voici un résumé des principales tendances : 

            - **Beaucoup de citoyens se plaignent de l'accessibilité des informations sur le web**, notamment la difficulté à trouver des informations fiables et à jour. D'autres se plaignent que le site est souvent en maintenance le soir.

            - **Les citoyens apprécient particulièrement la nouvelle fonctionnalité de chat en direct**, qui leur permet de poser des questions en temps réel.

            - **Les citoyens sont très satisfaits de leur accueil en mairie**, notant la gentillesse et la disponibilité du personnel.
            """)


        # Onglet 4 : Consulter - consulter les propositions des citoyens et rajouter une idée à pin
        with tab4:
            st.markdown("<div class='header'>➕ Consulter</div>", unsafe_allow_html=True)
            # Fonction pour charger les fichiers JSON
            def load_json(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except FileNotFoundError:
                    return []

            # Fonction pour sauvegarder dans les fichiers JSON
            def save_json(file_path, data):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

            # Charger les données
            verbatim_file = "data/propositions_maille_verbatim.json"
            pinned_ideas_file = "data/pinned_ideas.json"
            comments_file = "data/comments.json"

            verbatim_data = load_json(verbatim_file)
            pinned_ideas = load_json(pinned_ideas_file)
            comments = load_json(comments_file)

            # Ajouter une nouvelle idée
            new_title = st.text_input("Titre de l'idée", key="new_title")
            new_desc = st.text_area("Description de l'idée", key="new_desc")
            new_image = st.file_uploader("Uploader une image", type=["png", "jpg", "jpeg"], key="new_image")

            # Case à cocher pour chaque commentaire
            st.markdown("**Associez des commentaires existants à votre idée :**")
            selected_comments = []
            for i, comment in enumerate(verbatim_data):
                # Générer une clé unique en combinant l'indice et un hachage du texte du commentaire
                key = f"comment_{i}_{hash(comment['Proposition'])}"
                if st.checkbox(comment["Proposition"], key=key):
                    selected_comments.append(comment["Proposition"])

            if st.button("Soumettre", key="submit_new_idea"):
                if new_title and new_desc:
                    # Créer le chemin de l'image
                    image_folder = "images"
                    if not os.path.exists(image_folder):
                        os.makedirs(image_folder)
                    image_path = "images/default.jpg"
                    if new_image:
                        image_path = os.path.join(image_folder, new_image.name)
                        with open(image_path, "wb") as f:
                            f.write(new_image.read())

                    # Générer un nouvel ID incrémental
                    new_id = str(len(pinned_ideas) + 1)

                    # Ajouter la nouvelle idée au fichier pinned_ideas.json
                    new_idea = {
                        "ID": new_id,
                        "Titre de l'idée": new_title,
                        "Description de l'idée": new_desc,
                        "Nb likes": "0",
                        "Nb dislikes": "0",
                        "Fin du sondage": pd.Timestamp.now().strftime("%d/%m/%Y"),
                        "Path image": image_path,
                    }
                    pinned_ideas.append(new_idea)
                    save_json(pinned_ideas_file, pinned_ideas)

                    # Ajouter les commentaires associés au fichier comments.json
                    for comment in selected_comments:
                        comments.append({"Id_idea": new_id, "Comment": comment})
                    save_json(comments_file, comments)

                    # Confirmation de l'ajout
                    st.success("Votre idée a été ajoutée avec succès, avec les commentaires associés !")
                else:
                    st.error("Veuillez remplir tous les champs.")


    # Tab 5: Chat (todo)
    with tab5:
        st.markdown("<div class='header'>💬 Chat</div>", unsafe_allow_html=True)
