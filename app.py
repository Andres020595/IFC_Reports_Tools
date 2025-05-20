import streamlit as st
import pandas as pd
import tempfile
import io
from ifc_parser import load_ifc_file, get_elements_with_properties

st.set_page_config(page_title="IFC Report Tool", layout="wide")
st.title("📊 IFC Herramienta de reportes")

# Subir archivo IFC
uploaded_file = st.file_uploader("Sube un archivo IFC", type=["ifc"])

if uploaded_file:
    # Guardar archivo a temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.success("✅ Archivo cargado correctamente")

    # Cargar modelo IFC
    ifc_model = load_ifc_file(tmp_path)

    if ifc_model:
        # Extraer propiedades como DataFrame
        df = get_elements_with_properties(ifc_model)

        if not df.empty:
            st.subheader("Añadir columnas")

            # Mostrar lista de campos como checkboxes
            st.write("Selecciona los campos que deseas incluir en el reporte:")

            default_fields = {"GUID", "Name", "Type"}
            selected_columns = []

            cols_per_row = 3
            cols = st.columns(cols_per_row)

            for idx, column in enumerate(df.columns):
                with cols[idx % cols_per_row]:
                    checked = st.checkbox(column, value=(column in default_fields))
                    if checked:
                        selected_columns.append(column)

            # Previsualización
            filtered_df = df[selected_columns]
            st.subheader("Vista previa del Excel a exportar")
            st.dataframe(filtered_df, use_container_width=True)

            # Botón de exportación
            buffer = io.BytesIO()
            if st.button("📥 Exportar Excel"):
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name="Reporte IFC")
                st.download_button(
                    label="Descargar Excel",
                    data=buffer.getvalue(),
                    file_name="reporte_ifc.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("⚠️ No se encontraron elementos con propiedades.")
    else:
        st.error("❌ No se pudo cargar el archivo IFC.")
