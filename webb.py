import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# =============================
# PENGATURAN HALAMAN
# =============================


# Desain web
st.set_page_config(page_title="Analisis kemacetan lalu lintas", 
                   page_icon="📊",
                   layout="wide",
                   initial_sidebar_state="expanded")

# =============================
# PENGATURAN HALAMAN
# =============================
st.markdown("""
            <style>
            /* warna background utama */
            [data-testid="stAppViewContainer] {background: linear-gradient(
                135deg, 
                #1e1b2e, 
                #2d1b4e,
                #3b235f );
                color: white;}
                
            /* sidebar */ 
            [data-testid="stSidebar"] {background: linear-gradient(
                180deg,
                #2a163d,
                #3d1f5c,
                #4c1d95);}    
                     
            /* SEMUA TEKS */
            h1, h2, h3, h4, h5, h6, p, label {color: white!important; 
            text-align: center; }
            
            /* angka pada metric */ 
            [data-testid="stMetricValue"] 
            {font-size: 28px;
            color: green; font-weight: bold;} 
            
            /* tombol */ 
            div.stButton > button {
                background-color: #7c3aed;
                color: white;
                border-radius: 10px;
                border: nonne;
            } 
            /* B0X FILE UPLOAD & DROPDOWN */
            .stFileUploader,
            .stSelectbox {
                background-color;
                rgba(255,255,255,0.08);
                padding: 8px;
                border-radius: 10px;
            }
            /* TABEL DATA FRAME */
            [data-testid="stDataFrame] {
                background-color:
                rgba(225,225,225,0.05);
                border-radius: 10px;
            }
            
            </style>""", unsafe_allow_html=True)

# ==========================
# fungsi cronbach alpha
# ==========================
def cronbach_alpha(df):
    k = df.shape[1]
    varians_item = df.var(axis=0, ddof=1)
    varians_total = df.sum(axis=1).var(ddof=1)
    if varians_total == 0:
        return 0
    
    alpha = (k / (k - 1)) * (1 - varians_item.sum() / varians_total)
    return round(alpha, 3)

# ==========================
# judul web
# ==========================
st.title("KASI MASUK DISINI DATAMU")
st.write("upload file Excel atau CSV untuk dianalisis")

# ==========================
# upload file
# ==========================
st.sidebar.title("Menu")

uploaded_file = st.sidebar.file_uploader("Upload file Excel/CSV", type=["xlsx", "csv"])

# ==========================
# jika file ada
# ==========================
if uploaded_file is not None:
    
    # ================================
    # PILIHAN SHEET KHUSUS EXCEL
    # ================================
    if uploaded_file.name.endswith(".xlsx"):
        
        # baca nama semua sheet
        excel_file = pd.ExcelFile(uploaded_file)
        
        daftar_sheet = excel_file.sheet_names
        
        # dropdown pilihan sheet
        selected_sheet = st.selectbox("pilih sheet yang inginn di analisis", daftar_sheet)
        
        # baca sheet terpilih
        data = pd.read_excel(uploaded_file,sheet_name=selected_sheet)
        st.success(f"Sheet '{selected_sheet}' berhasil dibaca!")
        
        # ==================
        # TAMPILKAN DATA YANG DIUPLOAD
        # ============================
        st.subheader("1. informasi data")
        
        col1, col2 = st.columns(2)
        
        col1.metric("Jumlah Baris", data.shape[0])
        col2.metric("Jumlah Kolom", data.shape[1])
        if st.checkbox("Tampilkan seluruh data yang di upload"):
            st.dataframe(data)
            
        # hapus data
        data = data.dropna()
                    
    else:
        # kalau file csv
        data = pd.read_csv(uploaded_file)
        st.success("file CSV berhasil dibaca")
        
        # hapus data
        data = data.dropna()
    
    # =================================
    # DETEKSI PREFIX VARIABEL OTOMATIS
    # contoh: X1.1 -> X1
    # =================================
    prefixes = sorted(set(col.split('.')[0] for col in data.columns if '.' in col))
    
    st.subheader("2. Variabel Terdeteksi")
    st.write(prefixes)
    
    # =================================
    # HITUNG SKOR RATA-RATA TIAP AVRIABEL
    # =================================
    item_validitas = {}
    reliabilitas = {}
    
    for var in prefixes:
        kolom = [c for c in data.columns if c.startswith(var + ".")]
        
        # skor rata-rata variabel
        data[var] = data[kolom].mean(axis=1)
        
        # validitas item total
        total = data[var]
        
        hasil_validitas = {}
        for item in kolom:
            r = data[item].corr(total)
            hasil_validitas[item] = round(r, 3)
            
        item_validitas[var] = hasil_validitas
        
        # reliabilitas
        reliabilitas[var] = cronbach_alpha(data[kolom])
        
    # ===================
    # TAB MENU
    # ===================
    tab1, tab2, tab3, tab4 = st.tabs([
        "Ringkasan",
        "Validitas",
        "Korelasi",
        "Regresi"
     ])
        
    # =================================
    # RINGKASAN VARIABEL
    # =================================
    with tab1:
        
     st.subheader("3. Ringkasan Variabel")
    
    ringkasan = []
    
    for var in prefixes:
        
        # item milik variabel ini
        kolom = [c for c in data.columns if c.startswith(var + ".")]
        
        
        # jumlah_item
        jumlah_item = len(kolom)
        
        # mean
        mean_val = round(data[var].mean(), 3)
        
        # standar defiasi
        std_val = round(data[var].std(), 3)
        
        # cronbach alpha
        alpha = reliabilitas[var]
        
        # kategori berdasarkan mean
        if mean_val >= 4.21: kategori = "Sangat Tinggi"
        elif mean_val >= 3.41: kategori = "Tinggi"
        elif mean_val >= 2.61: kategori = "sedang"
        elif mean_val >= 1.81: kategori = "Rendah"
        else: kategori = "Sangat Rendah"
        
        ringkasan.append({
            "Variabel": var,
            "Jumlah item": jumlah_item,
            "Mean": mean_val,
            "Standar Defiasi": std_val,
            "cronbach alpha": alpha,
            "Kategori": kategori  
        })
        
    # buat data frame
    ringkasan_df = pd.DataFrame(ringkasan)
   
    # tampilkan
    st.dataframe(ringkasan_df)
        
    # =================================
    # VALIDITAS
    # =================================
    with tab2:
     st.subheader("5. Uji Validitas")
    
    for var in item_validitas:
        st.write(f"### {var}")
        valid_df = pd.DataFrame(item_validitas[var].items(),columns=["item", "r"])
        
        valid_df["status"] = valid_df["r"].apply(lambda x: "Valid" if x > 0.30 else "Tidak Valid")
        st.dataframe(valid_df)
        
    # =================================
    # RALIBILITAS
    # ================================= 
    st.subheader("6. Uji Reliabilitas")
    
    rel_df = pd.DataFrame(reliabilitas.items(), columns=["Variabel", "CronbachAlpha"])
    rel_df["status"] = rel_df["CronbachAlpha"].apply(lambda x: "Reliabel" if x >= 0.70 else "Tidak Reliabel")
    
    st.dataframe(rel_df)
    
    # =================================
    # KORELASI
    # ================================= 
    with tab3:
     st.subheader("7. Korelasi Antar Variabel")
    
    corr = data[prefixes].corr()
    st.dataframe(corr)
    
    # heatmap korelasi
    st.subheader("Grafik Korelasi (Heatmap)")
    fig, ax = plt.subplots(figsize=(8,6))
    
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    
    st.pyplot(fig)
    # =================================
    # REGRESI OTOMATIS
    # jika ada Y
    # ================================= 
    with tab4:
     if "Y" in prefixes:
        
        st.subheader("8. Regresi Linear")
        
        x_vars = [v for v in prefixes if v != "Y"]
        
        X = data[x_vars]
        y = data["Y"]
        
        model = LinearRegression()
        model.fit(X, y)
        
        # intercept
        st.write("intercep:",round(model.intercept_, 3))
        
        # koefisien
        coef_df = pd.DataFrame({"Variabel": x_vars, "Koefisien": model.coef_})
        st.dataframe(coef_df)
        
        st.write("### Koefisien Regresi")
        st.dataframe(coef_df)
        
        # R square
        r_square = model.score(X, y)
        
        st.write("### R Square")
        st.write(round(r_square, 3))
        
        # faktor utama
        faktor_utama = coef_df.loc[coef_df["Koefisien"].abs().idxmax()]
        
        st.write("### Faktor utama Yang Memengaruhi")
        st.write(f"Variabel utama yang memengaruhi kemacetan adalah "f"**{faktor_utama['Variabel']}** "f"dengan koefisien "f"**{round(faktor_utama['Koefisien'],3)}**")
        
        # =================================
        # INTERPRETASI FAKTOR UTAMA
        # =================================     
        st.subheader("Interpretasi Faktor Utama")
    
        nilai_koef = faktor_utama["Koefisien"]
        nama_var = faktor_utama["Variabel"]
    
        # Penjelasan umum
        st.write("Faktor utama ditentukan berdasarkan **nilai absolut "
                 "koefisien regresi terbesar**, sehingga variabel ini "
                 "dianggap memiliki pengaruh paling kuat terhadap kemacetan.")
    
         # arah pengaruh 
        if nilai_koef > 0:
             st.write(f"Koefisien variabel **{nama_var}** bernilai "f"positif (**{round(nilai_koef,3)}**). "f"Artinya tingkat kemacetan cenderung**meningkat**.")
        else:
            st.write(f"Koefisien Variabel **{nama_var}**bernilai "f"negatif (**negatif{round(nilai_koef, 3)}**). "f"Artinya, semakin tinggi nilai**{nama_var}**, "
                      "maka tingkat kemacetan cenderung**mmenurun**. ")
    
         # kesimpulan otomatis
        st.write(f"Dengan demikian, **{nama_var}** merupakan faktor "
                  "yang perlu menjadi perhatian utama dalam upaya "
                  "penanganan dan pengurangan kemacetan.")

        # grafik koefisien
        st.subheader("Grafik Pengaruh Variabel")
        
        fig, ax = plt.subplots()
        
        coef_df.set_index("Variabel").plot(kind="bar", ax=ax)
        
        plt.xticks(rotation=0)
        
        st.pyplot(fig)
    # =================================
    # VISUALISASI
    # ================================= 
    st.subheader("9. Grafik Rata-rata Variabel")
    
    fig, ax = plt.subplots()
    
    ringkasan_df.set_index("Variabel")["Mean"].plot(kind="bar", ax=ax)
    
    # tampilkan angka di atas batang
    for p in ax.patches:
        ax.annotate(str(round(p.get_height(), 2)),(p.get_x() + 0.1, p.get_height() + 0.02))
    
    plt.xticks(rotation=0)
    
    st.pyplot(fig)
    
    # =================================
    # SIMPAN HASIL
    # ================================= 
    output = "Hasil_Analisis.xlsx"
    data.to_excel(output, index=False)
    
    with open(output, "rb") as f:
        st.download_button("Download Hasilnya nichh",f,file_name="Hasil_analisis.xlsx")