from urllib.request import urlopen
from PIL import Image
from streamlit_cropper import st_cropper
import matplotlib.pyplot as plt
import streamlit as st

from data_access.data_access import get_image
from data_access.data_paths import get_figure_path
from data_viz.dl_plot import CLASSES, plot_mismatch_distribution, plot_pred_compare_with_truth, plot_predictions, predict_image
from session.state import increment_counter, init_session_states

# Présentation du contenu sur la sidebar
st.sidebar.markdown("# Présentation des CNN utilisés")
st.sidebar.write("""Dans cette partie, nous présentons les caractéristiques des divers réseaux de neurones testés ainsi que leurs performances.
Les résultats présentés sont ceux des transfer learning effectués à partir de chacun des modèles choisis. """)

COMMENTS = {
    "inceptionv3": """L’entraînement du modèle est effectué sur seulement 10 epochs 
        et nous obtenons une accuracy de 92% contre 90% sans fine-tuning avec un 
        temps d’entraînement d’environ 10 minutes. En revanche, nous remarquons 
        un overfitting assez important avec ce modèle.""",

    "vgg16": """L’entraînement du modèle est effectué sur seulement 10 epochs mais 
    se stoppe à 6 epochs car l’accuracy n’évolue plus et nous obtenons une accuracy 
    de 95% contre 94% sans fine-tuning avec un temps d’entraînement d’environ 10 
    minutes. En revanche, nous remarquons un léger overfitting avec ce modèle""",

    "dense_net": """L’entraînement du modèle est effectué sur seulement 25 epochs et 
    nous obtenons une accuracy de 98% contre 95% sans fine-tuning avec un temps 
    d’entraînement d’environ 50 minutes.""",

    "basic_model": """L’entraînement du modèle est effectué jusqu’à ce que l’accuracy 
    de validation augmente de moins de 0.1% sur 10 epochs, avec également un mécanisme 
    de réduction du taux d’apprentissage en cas de détection de plateau. Nous obtenons 
    une accuracy de 96% avec un temps d’entraînement d’environ 30 minutes. Nous 
    constatons que le phénomène de divergence précédemment observé se reproduit, 
    mais plus tard, à partir de la 20ème epoch environ. De plus, il est moins prononcé, 
    l’accuracy d’entraînement montant jusqu’aux alentours de 99% tandis que celle de 
    validation plafonne autour de 96% à partir de la 25ème epoch environ."""
}

urls_by_cell_type = {'basophil': [
    "https://imagebank.hematology.org/getimagebyid/60504?size=3",
    "https://imagebank.hematology.org/getimagebyid/60505?size=3",
    "http://medcell.org/histology/blood_bone_marrow_lab/images/basophil.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Basophile-9.JPG/375px-Basophile-9.JPG",
],
    "eosinophil": [
        "http://imagebank.hematology.org/getimagebyid/60934?size=3",
        "http://imagebank.hematology.org/getimagebyid/60933?size=2",
        "http://www.hkimls.org/eos1.jpg",
        "http://www.hkimls.org/eos2.jpg"
],
    'erythroblast': [
        "https://www.cellavision.com/images/Hematopoiesis/Erythropoiesis/PolychromaticErythroblast/POLYCHROMATICERYTHROBLAST1.jpg",
        "https://www.cellavision.com/images/Hematopoiesis/Erythropoiesis/OrthochromaticErythroblast/ORTHROCHROMATICERYTHROBLAST1.jpg",
],
    'ig': ["A compléter"],
    'lymphocyte': ["A compléter"],
    'monocyte': ["A compléter"],
    'neutrophil': [
        "http://imagebank.hematology.org/getimagebyid/61935?size=2"
],
    'platelet': ["A compléter"]}


def get_section(model_name, img_size=256):
    def section():
        st.markdown(f"# Modèle de transfer learning avec {model_name}")
        st.markdown("## Paramètres du modèle et résultats")
        st.write(4*"\n")

        # image du résumé du modèle
        network_img = get_image(get_figure_path(f"{model_name}_summary"))
        st.image(network_img, width=800)
        st.write(COMMENTS[model_name])

        # image du rapport de classification
        classification_report = get_image(
            get_figure_path(f"rapport_classification_{model_name}"))
        _, col2, _ = st.columns([0.2, 1, 0.2])
        col2.image(classification_report, use_column_width=True, width=200)

        # image de la courbe accuracy
        curve_img = get_image(get_figure_path(f"courbe_{model_name}"))
        _, col2, _ = st.columns([0.2, 0.5, 0.2])
        col2.image(curve_img, use_column_width=True, width=200)

        st.markdown("## Etude des erreurs faites par le modèle")
        st.markdown("### Répartition")

        fig, mismatch_df = plot_mismatch_distribution(model_name)
        st.write(
            f"Il y a en tout {len(mismatch_df)} images mal classées pour ce modèle.")
        st.pyplot(fig)

        st.markdown("### Visualisation")
        true_cell_type = st.selectbox("Type cellulaire réel:", CLASSES)
        cell_type_mimatch_df = mismatch_df[mismatch_df.true_cell_type ==
                                           true_cell_type]

        pred_cell_type = st.selectbox(
            "Type cellulaire prédit:", cell_type_mimatch_df.predicted_cell_type.unique())

        pred_cell_type_mimatch_df = cell_type_mimatch_df[
            cell_type_mimatch_df.predicted_cell_type == pred_cell_type].reset_index(drop=True)

        l = len(pred_cell_type_mimatch_df)
        st.write(
            f"Le type cellulaire {true_cell_type} est confondu {l} fois avec le type cellulaire {pred_cell_type}.")

        fig = plot_pred_compare_with_truth(pred_cell_type_mimatch_df)
        st.pyplot(fig)

        st.markdown("## Inférence sur images du jeu de données original")
        pred_counter_key = f'{model_name}_prediction_counter'

        init_session_states(pred_counter_key)

        st.markdown("### Jeux de données original")
        col_1_1, col_1_2 = st.columns(2)
        pred_counter = st.session_state[pred_counter_key]
        fig_1_1, fig_1_2, correctness, prediction = plot_predictions(
            model_name, pred_counter, img_size)
        with col_1_1:
            img_placeholder = st.empty()
            img_placeholder.pyplot(fig_1_1)

        with col_1_2:
            barplot_placeholder = st.empty()
            barplot_placeholder.pyplot(fig_1_2)

            st.write(
                f"La prediction est {correctness} comme probable à {prediction.max()*100:.0f}%.")

        st.button("reload", on_click=increment_counter,
                  args=(pred_counter_key,))

        st.markdown(
            "## Images externes au jeu de données original")
        cell_type = st.selectbox(
            "Type cellulaire", CLASSES)
        url = st.selectbox("Images", urls_by_cell_type[cell_type])

        test_img = Image.open(urlopen(url))
        w, h = test_img.size
        max_width = 350
        test_img = test_img.resize((max_width, h * max_width // w))
        col1, col2 = st.columns(2)
        with col1:
            cropped_img = st_cropper(test_img, realtime_update=True, box_color='black',
                                     aspect_ratio=(1, 1))
        with col2:

            fig, ax = plt.subplots()
            probas = predict_image(model_name, cropped_img)
            pred_index = probas.argmax()
            ax.bar(CLASSES, height=probas)
            ax.tick_params(axis='x', labelrotation=45)
            st.pyplot(fig)
            correctness = "correcte et estimée" if cell_type == CLASSES[
                pred_index] else "incorrecte, bien qu'estimée"
            st.write(
                f"La prediction est {correctness} comme probable à {probas.max()*100:.0f}%.")

    return section


page_names_to_funcs = {
    "DenseNet121": get_section("dense_net"),
    "Basic Model": get_section("basic_model", img_size=64),
    "VGG16": get_section("vgg16"),
    "InceptionV3": get_section("inceptionv3"),
}

selected_page = st.sidebar.selectbox(
    "Select a page", page_names_to_funcs.keys())

page_names_to_funcs[selected_page]()