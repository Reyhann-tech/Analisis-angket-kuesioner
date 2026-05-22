import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

from scipy.stats import shapiro
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
import statsmodels.api as sm

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
                background-color:
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
key = "upload_data"

# ==========================
# jika file ada
# ==========================
if uploaded_file is not None:
    
    # ===========================
    # PILIHAN SHEET KHUSUS EXCEL
    # ===========================
    if uploaded_file.name.endswith(".xlsx"):
        
        # ===========================
        # baca nama semua sheet
        # ===========================
        excel_file = pd.ExcelFile(uploaded_file)
        
        daftar_sheet = excel_file.sheet_names
        
        # ===========================
        # dropdown pilihan sheet
        # ===========================
        selected_sheet = st.selectbox("pilih sheet yang ingin di analisis", daftar_sheet)
        
        # ===========================
        # baca sheet terpilih
        # ===========================
        data = pd.read_excel(uploaded_file,sheet_name=selected_sheet)
        st.success(f"Sheet '{selected_sheet}' berhasil dibaca!")
        
        # ===========================
        # TAMPILKAN DATA YANG DIUPLOAD
        # ===========================
        st.subheader("1. informasi data")
        
        col1, col2 = st.columns(2)
        
        col1.metric("Jumlah Baris", data.shape[0])
        col2.metric("Jumlah Kolom", data.shape[1])
        if st.checkbox("Tampilkan seluruh data yang di upload"):
            st.dataframe(data)
        
        # ===========================    
        # hapus data
        # ===========================
        data = data.dropna()
                    
    else:
        # ===========================
        # kalau file csv
        # ===========================
        data = pd.read_csv(uploaded_file)
        st.success("file CSV berhasil dibaca")
        
        # ===========================
        # hapus data
        # ===========================
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
        
        # ===========================
        # skor rata-rata variabel
        # ===========================
        data[var] = data[kolom].mean(axis=1)
        
        # ===========================
        # validitas item total
        # ===========================
        total = data[var]
        
        hasil_validitas = {}
        for item in kolom:
            r = data[item].corr(total)
            hasil_validitas[item] = round(r, 3)
            
        item_validitas[var] = hasil_validitas
        
        # ===========================
        # reliabilitas
        # ===========================
        reliabilitas[var] = cronbach_alpha(data[kolom])
        
    # ===================
    # TAB MENU
    # ===================
    # tab1, tab2, tab3, tab4 = st.tabs([
    #     "Ringkasan",
    #     "Validitas",
    #     "Korelasi",
    #     "Regresi"
    #  ])
        
    # =================================
    # RINGKASAN VARIABEL
    # =================================
    # with tab1:    
    st.subheader("3. Ringkasan Variabel")
    
    ringkasan = []
    
    for var in prefixes:
        
        # ===========================
        # item milik variabel ini
        # ===========================
        kolom = [c for c in data.columns if c.startswith(var + ".")]
        
        # ===========================
        # jumlah_item
        # ===========================
        jumlah_item = len(kolom)
        
        # ===========================
        # mean
        # ===========================
        mean_val = round(data[var].mean(), 3)
        
        # ===========================
        # standar defiasi
        # ===========================
        std_val = round(data[var].std(), 3)
        
        # ==========================
        # cronbach alpha
        # ==========================
        alpha = reliabilitas[var]
        
        # ===========================
        # kategori berdasarkan mean
        # ===========================
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
    # =========================    
    # buat data frame
    # =========================
    ringkasan_df = pd.DataFrame(ringkasan)
   
    # ===========================
    # tampilkan
    # ===========================
    st.dataframe(ringkasan_df)
        
    # =================================
    # VALIDITAS
    # =================================
    # with tab2:
    st.subheader("4. Uji Validitas")
    
    for var in item_validitas:
        st.write(f"### {var}")
        valid_df = pd.DataFrame(item_validitas[var].items(),columns=["Item", "r"])
        
        valid_df["status"] = valid_df["r"].apply(lambda x: "Valid" if x > 0.30 else "Tidak Valid")
        st.dataframe(valid_df)
        
    # =================================
    # RALIBILITAS
    # ================================= 
    st.subheader("5. Uji Reliabilitas")
    
    rel_df = pd.DataFrame(reliabilitas.items(), columns=["Variabel", "CronbachAlpha"])
    rel_df["status"] = rel_df["CronbachAlpha"].apply(lambda x: "Reliabel" if x >= 0.70 else "Tidak Reliabel")
    
    st.dataframe(rel_df)
    
    # =================================
    # KORELASI
    # ================================= 
    # with tab3:
    st.subheader("6. Korelasi Antar Variabel")
    
    corr = data[prefixes].corr()
    st.dataframe(corr)
    
    # ===========================
    # heatmap korelasi
    # ===========================
    st.subheader("Grafik Korelasi (Heatmap)")
    fig, ax = plt.subplots(figsize=(8,6))
    
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    
    st.pyplot(fig)
    
    # interpretasi korelasi
    st.subheader("Penjelasan Korelasi")
    
    corr_copy = corr.copy()
    
    # hilangkan diagonal (1.00)
    for col in corr_copy.columns:
        corr_copy.loc[col, col] = 0
        
    # cari korelasi terbesar
    max_corr = corr_copy.abs().stack().idxmax()
    
    var1 = max_corr[0]
    var2 = max_corr[1]
    
    nilai_korelasi = corr.loc[var1, var2]
    
    # kategori kekuatan
    nilai_abs = abs(nilai_korelasi)
    
    if nilai_abs >= 0.80:
        kategori = "sangat kuat"
    elif nilai_abs >= 0.60:
        kategori = "kuat"
    elif nilai_abs >= 0.40:
        kategori = "sedang"
    elif nilai_abs >= 0.20:
        kategori = "lemah"
    else:
        kategori = "sangat lemah"
        
    # arah hubungan
    if nilai_korelasi > 0:
        arah = "positif"
    else:
        arah = "negatif"
        
    st.info(f"""
            Hubungan paling tinggi ditemukan antara
            **{var1}** dan **{var2}**
            dengan nilai korelasi
            **{round(nilai_korelasi,3)}**.
            
            Hubungan ini termasuk kategori **{kategori}**
            dan memiliki arah **{arah}**.
            
            Interpretasi umum:
            
            • 0.00-0.19  →  Sangat lemah
            
            • 0.20-0.39  →  Lemah
            
            • 0.40-0.59  →  Sedang
            
            • 0.60-0.79  →  Kuat
            
            • 0.80-1.00  →  Sangat kuat
            
            Korelasi positif → kedua variabel cenderung meningkat bersama.
            
            korelasi negatif → satu variabel meningkat sementara variabel lain menurun
            """)
    # =================================
    # REGRESI OTOMATIS
    # jika ada Y
    # ================================= 
    # with tab4:
    if "Y" in prefixes:
        
        st.subheader("7. Regresi Linear")
        
        x_vars = [v for v in prefixes if v != "Y"]
        
        X = data[x_vars]
        y = data["Y"]
        
        model = LinearRegression()
        model.fit(X, y)
        
        # ===========================
        # intercept
        # ===========================
        st.write("intercep:",round(model.intercept_, 3))
        
        # ===========================
        # koefisien
        # ===========================
        coef_df = pd.DataFrame({"Variabel": x_vars, "Koefisien": model.coef_})
        st.dataframe(coef_df)
        
        st.write("### Koefisien Regresi")
        st.dataframe(coef_df)
        
        # ===========================
        # R square
        # ===========================
        r_square = model.score(X, y)
        
        st.write("### R Ringkasan Statistik")
        
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Jumlah Variabel", len(x_vars))
        
        col2.metric("Jumlah responden", data.shape[0])
        
        col3.metric("R² Model", round(r_square, 3))
        
        # ===========================
        # AUTO INTERPRETASI UNIVERSAL
        # ===========================
        st.subheader("Interpretasi Hasil Regresi")
        idx = coef_df["Koefisien"].abs().idxmax()
        
        faktor_utama = coef_df.loc[idx, "Variabel"]
        nilai_coef = coef_df.loc[idx, "Koefisien"]

        # =================================
        # ARAH PENGARUH
        # ================================= 
        if nilai_coef > 0:
            arah = "meningkatkan"
            efek = "berpengaruh positif"
        else:
            arah = "menurunkan"
            efek = "berpengaruh negatif"
            
        # ===========================
        # KUALITAS MODEL berdasarkan r2
        # ===========================
        if r_square >= 0.75:
            kualitas = "sangat kuat"
        elif r_square >= 0.50:
            kualitas = "kuat"
        elif r_square >= 0.25:
            kualitas = "cukup"
        else:kualitas = "lemah"
       
        interpretasi = f""" 
        <div style="
        padding:20px; 
        background: rgba(255,255,255,0.05);
        border-radius:15px;
        line-height:1.8;
        text-align:left;
        font-size:16px;">
        
        <p>
        Hasil analisis menunjukkan bahwa 
        <b>{faktor_utama}</b> merupakan variabel yang paling dominan dalam model.
        </p>
        
        <p>
        Variabel tersebut memiliki nilai koefisien sebesar <b>{round(nilai_coef,3)}</b>, 
        yang menunjukkan bahwa variabel ini <b>{efek}</b> terhadap variabel target.
        </p>
        
        <p>
        Artinya, setiap peningkatan pada variabel tersebut akan cenderung <b>{arah}</b> nilai variabel target.
        </p>
        
        <p>
        Model regresi memiliki nilai <b>R² = {r_square:.3f}</b>, sehingga kemampuan model dalam 
        menjelaskan variasi data termasuk kategori <b>{kualitas}</b>.
        </p>
        
        <p>
        Secara keseluruhan, variabel-variabel dalam model memiliki pengaruh terhadap 
        variabel target sesuai dengan kekuatan model yang diperoleh.
        </p>
        
        </div>"""
        
        st.markdown(interpretasi, unsafe_allow_html=True)
        
        # ===========================
        # kesimpulan otomatis
        # ===========================
        st.subheader(" Kesimpulan Otomatis")
        
        #kualitas model
        if r_square >= 0.75:
            kualitas_model = "sangat kuat"
        elif r_square >= 0.50:
            kualitas_model = "kuat"
        elif r_square >= 0.25:
            kualitas_model = "cukup"
        else:
            kualitas_model = "lemah"
            
        kesimpulan = f"""
        Berdasarkan hasil analisis regresi yang dilakukan, diketahui bahwa variabel
        **{faktor_utama}** merupakan faktor yang memiliki pengaruh paling dominan
        dalam model penelitian dengan nilai koefisien sebesar **{round(nilai_coef,3)}**.
        
        Model regresi yang dibentuk memiliki nilai **R² = {round(r_square,3)}**,
        yang menunjukkan bahwa kemampuan model dalam menjelaskan variasi variabel 
        target termasuk kategori **{kualitas_model}**.
        
        Hasil uji asumsi menunjukkan bahwa model telah melalui pengujian nimalitas, multikolinearitas, dan
        heteroskedastisitas.
        
        Secara keseluruhan, variabel-variabel penelitian memiliki kontribusi terhadap
        variabel target sesuai kekuatan model yang diperoleh."""
        
        st.success(kesimpulan)
         
        # ===========================
        # grafik koefisien
        # ===========================
        st.subheader("Grafik Pengaruh Variabel")
        
        fig, ax = plt.subplots()
        
        coef_df.set_index("Variabel").plot(kind="bar", ax=ax)
        
        plt.xticks(rotation=0)
        
        st.pyplot(fig)
        
    # =================================
    # UJI ASUMSI REGREASI
    # =================================     
    st.subheader("8. Uji Asumsi Regresi")    
        
    # hiitung residual
    prediksi = model.predict(X)
    residual = y - prediksi
    
    # uji normalitas
    st.write("### Uji Normalitas(Shapiro-Wilk)")
    
    stat, p = shapiro(residual)
    
    if p > 0.05:
        hasil_normal = "Residu berdistribusi normal"
    else:
        hasil_normal = "Residu tidak berdurasi normal"
        
    st.write(
        f"P-value = {round(p,4)} → {hasil_normal}"
    )    
    
    # uji multikolinearitas
    st.write("### Uji Multikolinearitas (VIF)")
    
    X_vif = sm.add_constant(X)
    
    vif_data = []
    
    for i in range(X_vif.shape[1]):
        
        vif = variance_inflation_factor(X_vif.values, i)
        
        vif_data.append([X_vif.columns[i],
                         round(vif, 3)])
        
    vif_df = pd.DataFrame(vif_data, columns=["Variabel","VIF"])
        
    vif_df = vif_df[vif_df["Variabel"] != "const"]
        
    vif_df["Status"] = vif_df["VIF"].apply(lambda x: "Aman" if x < 10 else "Tinggi")
        
    st.dataframe(vif_df)
        
    # uji heteroskedastisitas
    st.write("### Uji Heteroskedastisitas")
    
    bp_test = het_breuschpagan(residual, X_vif)
    
    p_bp = bp_test[1]
    if p_bp > 0.05:
        hasil_bp = "Tidak terdapat heteroskedastisitas"
    else:
        hasil_bp = "Terdapat heteroskedastisitas"
        
    st.write(f"P-value = {round(p_bp,4)} → {hasil_bp} ")    
        
        
    # =================================
    # VISUALISASI
    # ================================= 
    st.subheader("9. Grafik Rata-rata Variabel")
    
    fig, ax = plt.subplots()
    
    ringkasan_df.set_index("Variabel")["Mean"].plot(kind="bar", ax=ax)
    
    # ===========================
    # tampilkan angka di atas batang
    # ===========================
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
    # tab1, tab2, tab3, tab4 = st.tabs([
    #     "Ringkasan",
    #     "Validitas",
    #     "Korelasi",
    #     "Regresi"
    #  ])
        
    # =================================
    # RINGKASAN VARIABEL
    # =================================
    # with tab1:
        
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
    # with tab2:
    st.subheader("4. Uji Validitas")
    
    for var in item_validitas:
        st.write(f"### {var}")
        valid_df = pd.DataFrame(item_validitas[var].items(),columns=["item", "r"])
        
        valid_df["status"] = valid_df["r"].apply(lambda x: "Valid" if x > 0.30 else "Tidak Valid")
        st.dataframe(valid_df)
        
    # =================================
    # RALIBILITAS
    # ================================= 
    st.subheader("5. Uji Reliabilitas")
    
    rel_df = pd.DataFrame(reliabilitas.items(), columns=["Variabel", "CronbachAlpha"])
    rel_df["status"] = rel_df["CronbachAlpha"].apply(lambda x: "Reliabel" if x >= 0.70 else "Tidak Reliabel")
    
    st.dataframe(rel_df)
    
    # =================================
    # KORELASI
    # ================================= 
    # with tab3:
    st.subheader("6. Korelasi Antar Variabel")
    
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
    # with tab4:
    if "Y" in prefixes:
        
        st.subheader("7. Regresi Linear")
        
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
    st.subheader("8. Grafik Rata-rata Variabel")
    
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
