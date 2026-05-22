# ====================
# IMPORT LIBRARY
# ====================
import openpyxl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# ====================
# 1. BACA FILE EXCEL
# ====================
data = pd.read_excel('data_kuesioner.xlsx')

print("===  DATA AWAL  ===")
print(data.head())

# ====================
# 2. CEK DATA
# ====================
print("\n=== INFO DATA ===")
print(data.info())

data = data.dropna()

# ====================
# 3. KELOMPOK VARIABEL
# ====================
X1 = data[['X1.1','X1.2','X1.3','X1.4','X1.5']]
X2 = data[['X2.1','X2.2','X2.3','X2.4','X2.5']]
X3 = data[['X3.1','X3.2','X3.3','X3.4','X3.5']]
X4 = data[['X4.1','X4.2','X4.3','X4.4','X4.5']]
Y = data[['Y.1','Y.2','Y.3', 'Y.4', 'Y.5']]
Z = data[['Z.1','Z.2','Z.3','Z.4','Z.5']]
 
# ====================
# 4.HITUNG SKO RATA"
# ===================
data['X1'] = X1.mean(axis=1)
data['X2'] = X2.mean(axis=1)
data['X3'] = X3.mean(axis=1)
data['X4'] = X4.mean(axis=1)
data['Y'] = Y.mean(axis=1)
data['Z'] = Z.mean(axis=1)

print("\n=== SKOR VARIABEL ===")
print(data[['X1', 'X2', 'X3', 'X4', 'Y', 'Z']].head())
 
# ====================
# 5. ANALISIS DESKRIPTIF
# ====================
print("\n=== RATA-RATA VARIABEL ===")
print(data[['X1', 'X2', 'X3', 'X4', 'Y', 'Z']].mean())

print("\n=== STANDAR DEVIASI ===")
print(data[['X1', 'X2', 'X3', 'X4', 'Y', 'Z']].std())

# ====================
# 6. UJI VALIDITAS
# ====================
def uji_validitas(df, nama):
    print(f"\n=== VALIDITAS {nama} ===")
    total = df.mean(axis=1)
    
    for col in df.columns:
        r = df[col].corr(total)
        print(f"{col}: {round(r,3)}")
        
uji_validitas(X1, "X1")
uji_validitas(X2, "X2")
uji_validitas(X3, "X3")
uji_validitas(X4, "X4")
uji_validitas(Y, "Y")
uji_validitas(Z, "Z")

# ====================
# 7. UJI RELIBIALITAS
# ====================
def cronbach_alpha(df):
    item_var = df.var(axis=0, ddof=1)
    total_var = df.sum(axis=1).var(ddof=1)
    n = df.shape[1]
    
    alpha = (n / (n - 1)) * (1 - (item_var.sum() / total_var))
    return alpha

print("\n=== RELIBILITAS ===")
print("X1:", round(cronbach_alpha(X1),3))
print("X2:", round(cronbach_alpha(X2),3))
print("X3:", round(cronbach_alpha(X3),3))
print("X4:", round(cronbach_alpha(X4),3))
print("Y :", round(cronbach_alpha(Y),3))
print("Z :", round(cronbach_alpha(Z),3))

# ====================
# 8. KORELASI ANTAR VARIABEL
# ====================
print("\n=== KORELASI VARIABEL ===")
corr = (data[['X1', 'X2', 'X3', 'X4', 'Y', 'Z']].corr())
print(corr)

# ====================
# 9. REGRESI LINEAR
# ====================
X = data[['X1','X2','X3','X4']]
target = data['Y']

model = LinearRegression()
model.fit(X, target)

print("\n=== HASIL REGRESI ===")
print("Intercept:", round(model.intercept_))
print("koefisien X1:", round(model.coef_[0],3))
print("koefisien X2:", round(model.coef_[1],3))
print("koefisien X3:", round(model.coef_[2],3))
print("koefisien X4:", round(model.coef_[3],3))

# ====================
# 10. VISUALISASI
# ====================
data[['X1','X2','X3','X4','Y','Z']].mean().plot(kind='bar')

plt.title("Rata-rata Variabel Kuesioner")
plt.xlabel("Variabel")
plt.ylabel("nilai")
plt.tight_layout()
plt.show()

# ====================
# 11. HASIL
# ====================
data.to_excel('hasil_analisis kuesioner.xlsx', index=False)

print("\nfile berhasil disimpan:")
print("hasil_analisis kuesioner.xlsx")





