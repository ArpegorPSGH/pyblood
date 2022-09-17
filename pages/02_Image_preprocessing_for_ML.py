import streamlit as st
from data_viz.plot import plot_select_percentile_mask, reload_content, plot_color_and_bg_img, multi_sized_images


# Présentation du contenu sur la sidebar
st.sidebar.markdown("# Prétraitement des images")
st.sidebar.write("""On présente ici le travail fait sur le jeux de données initial 
et sur les images pour optimiser la quantité et la qualité des données.""")


# Chaque section est contenue dans une fonction
def resampling():
    st.markdown("## Rééchantillonnage du jeux de données")
    st.write("à compléter")


def image_reduction():
    st.markdown("## Réduction de la taille des données")

    st.markdown('### Images en niveaux de gris')
    st.write("""Etant donnée l'homogénéité du jeux de données en termes de
    palette de couleurs présente dans chaque image, on a estimé que se
    contenter de la version noir et blanc des images ne devrait pas représenter
    une grosse perte d'information.""")

    fig_placeholder = st.empty()
    fig = plot_color_and_bg_img()
    fig_placeholder.pyplot(fig)

    st.button(
        "Charger une autre image",
        key=1,
        on_click=reload_content,
        args=(fig_placeholder.pyplot, plot_color_and_bg_img))
    st.markdown('### Différentes tailles pour les images')

    st.write("""D'abord dans une volonté de pouvoir rapidement tester les algorithmes
    on a généré des jeux de données contenant les images en noir et blanc et en
    tailles réduites : de 30x30 à 200x200""")

    placeholder = st.empty()
    placeholder.pyplot(multi_sized_images())

    st.button(
        "Charger d'autres images",
        key=2,
        on_click=reload_content,
        args=(placeholder.pyplot, multi_sized_images))

    st.write("""Lors des tests des différents algorithmes, on s'est rendu compte que
    réduire la taille de l'image avait un réel impact sur la qualité de la prédiction
    qu'au delà de 70x70.""")


def feature_selection():
    st.markdown("## Selection de features")

    st.markdown("### SelectPercentile")
    st.write("""Dans un premier temps on a utilisé l'algorithme SelectPercentile de la
    bibliothèque scikit-learn.""")
    st.write("""Ce dernier effectue un test ANOVA entre les pixels de l'image et leur label
    puis retourne un tableau contenant le score de chaque pixel si celui-ci
    est dans le top 10 pour cent (valeur par défaut)  et 0 sinon.
    On peut alors construire un masque permettant de retenir les pixels
    obtenant les meilleurs scores.""")

    size = st.selectbox("Taille des images :", [200, 100, 70, 50, 30], index=2)

    fig_placeholder = st.empty()
    fig = plot_select_percentile_mask(size)

    fig_placeholder.pyplot(fig)

    st.button(
        "Charger une autre image",
        key=3,
        on_click=reload_content,
        args=(fig_placeholder.pyplot, plot_select_percentile_mask, size))

    st.markdown("### Rognage automatique")
    st.write("à compléter")


def dimension_reduction():
    st.markdown("## Réduction de dimension")
    st.markdown("### PCA")
    st.write("à compléter")
    st.markdown("### LDA")
    st.write("à compléter")


# Ce bloc de code permet de passer d'une section à une autre via la dropbox de la sidebar
page_names_to_funcs = {
    "Rééchantillonage du jeux de données": resampling,
    "Réduction de la taille des images": image_reduction,
    "Selection de features": feature_selection,
    "réduction de dimension": dimension_reduction
}

selected_page = st.sidebar.selectbox(
    "Section : ", page_names_to_funcs.keys())

page_names_to_funcs[selected_page]()
