import streamlit as st
import pandas as pd
import base64


def get_csv_download_link(df, filename="donnees_reechantillonnees.csv"):
    # Ajoutez l'indice (la colonne Date) au fichier CSV
    df_with_index = df.copy()
    df_with_index.reset_index(inplace=True)

    csv = df_with_index.to_csv(index=False, sep=';')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Télécharger les données rééchantillonnées</a>'
    return href



def fonction_de_reechantillonage(df, colonnes, frequence, fonction_agregation):
 
    # Sélectionnez les colonnes spécifiées
    df_selection = df[colonnes]
 
    # Remplacer la virgule par un point dans chaque colonne
    for col in df_selection.columns:
        df_selection[col] = pd.to_numeric(df_selection[col].str.replace(',', '.'), errors='coerce')
 
    # Appliquez la méthode resample avec la fonction d'agrégation spécifiée
    df_reechantillonne = df_selection.resample(frequence).agg(fonction_agregation)
 
    return df_reechantillonne

uploaded_file = st.file_uploader('Téléchargez votre fichier CSV (séparateur: point-virgule, UTF-8)', type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=';')
        #st.write(df.head())
        # Afficher les noms des colonnes pour que l'utilisateur puisse choisir
        date_columns = st.multiselect('Choisissez les colonnes qui représentent la période (date et/ou heure):', df.columns)

        if date_columns:
            # Concaténer les colonnes sélectionnées pour former la colonne 'Date'
            df.insert(0, 'Time',df[date_columns].apply(lambda row: ' '.join(row.values.astype(str)), axis=1) )
            # Supprimer les colonnes utilisées pour former la date
            df = df.drop(columns=date_columns)

            # Vous pouvez convertir la colonne 'Date' en datetime si nécessaire
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
            # Définir la colonne 'Time' comme nouvel index du DataFrame
            df.set_index('Time', inplace=True)

        #st.write(df.head())  # Afficher les premières lignes pour vérifier

    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        st.stop()

   # Afficher les données brutes
    st.subheader('Données brutes:')
    st.write(df)

    # Permettre à l'utilisateur de choisir les colonnes
    selected_columns = st.multiselect('Sélectionnez les colonnes à rééchantillonner:', df.columns)

    # Permettre à l'utilisateur de choisir l'unité de fréquence de rééchantillonnage
    resampling_unit = st.selectbox('Sélectionnez l\'unité de fréquence de rééchantillonnage:', ['minutes', 'heures', 'jours'], index=1)

    # Permettre à l'utilisateur d'entrer la valeur de fréquence de rééchantillonnage
    resampling_value = st.number_input('Entrez la valeur de fréquence de rééchantillonnage:', min_value=1, value=1)

    # Permettre à l'utilisateur de choisir la fonction d'agrégation
    aggregation_function = st.selectbox('Sélectionnez la fonction d\'agrégation:', ['sum', 'mean','min','max'], index=1)

    # Afficher les données rééchantillonnées
    if st.button('Rééchantillonner les données'):
        if not selected_columns:
            st.warning('Veuillez sélectionner au moins une colonne.')
        else:
            # Mapper l'unité sélectionnée à la chaîne de fréquence appropriée de pandas
            mapping_unite_frequence = {'minutes': 'T', 'heures': 'H', 'jours': 'D'}
            frequence_reechantillonnage = f'{resampling_value}{mapping_unite_frequence[resampling_unit]}'

            # Appeler la fonction de rééchantillonnage
            df_reechantillonnee = fonction_de_reechantillonage(df, selected_columns, frequence_reechantillonnage, aggregation_function)

            # Afficher les données rééchantillonnées
            st.subheader('Données rééchantillonnées:')
            st.write(df_reechantillonnee)
            st.markdown(get_csv_download_link(df_reechantillonnee), unsafe_allow_html=True)
