import streamlit as st
from scripts.ingest_data import ingest_hist_data_streamlit, default_file_name
from scripts.batch_model import train_test_model

st.set_page_config(page_title="Train static model", page_icon="⚙️")
st.title('⚙️ Train static model')

option = st.radio("Pick an option:", ("Download data", "Train and test a model"))

if option == "Download data":
    st.subheader("Download data")
    default_name = default_file_name()
    file_name = st.text_input("Nom du fichier (inclure .csv) :", default_name)

    if st.button("Download"):
            with st.spinner('Downloading the data...'):
                try:
                    ingest_hist_data_streamlit(default_name)
                    st.success(f"File successfully downloaded")
                except Exception as e:
                    st.error(f"Download error : {e}")


elif option == "Train and test a model":
    st.subheader("Train and test a model")
    default_file = "Data/DEFINITIVE_2025-01-10_2025-01-17_past_data_with_Y.csv"
    uploaded_file = st.file_uploader("Upload a CSV file for training (if nothing, use the default file):", type=["csv"])

    if uploaded_file:
        file_to_use = uploaded_file
        st.info(f"File loaded: {uploaded_file.name}")
    else:
        file_to_use = default_file
        st.warning(f"No file loaded. Use default file: {default_file}")

    save = st.checkbox("Do you want to save the model and graphics?", value=False)
    if st.button("Train and test"):
        with st.spinner('Training and testing the model...'):
            try:
                mse_train, mse_test, r2_train, r2_test = train_test_model(file_to_use, save=save)
                st.subheader("Model performance")
                st.write(f"Train MSE : {mse_train:.4f}")
                st.write(f"Test MSE : {mse_test:.4f}")
                st.write(f"Train R² : {r2_train:.4f}")
                st.write(f"Test R² : {r2_test:.4f}")
            except Exception as e:
                st.error(f"Training error: {e}")

        
