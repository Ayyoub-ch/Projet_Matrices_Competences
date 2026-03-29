import pandas as pd
import mysql.connector
import re
import soft_skills
import os

# === Configuration ===
fichier_path = "Matrices"
feuille_soft = "Matrice soft skills"

# === Connexion MySQL ===
def connexion_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )

# === Lecture du fichier Excel ===
def lire_excel(fichier_path):
    try:
        excel_file = pd.ExcelFile(fichier_path)

        df_soft_meta = pd.read_excel(excel_file, sheet_name=feuille_soft, header=None)
        nom_prenom_cell = df_soft_meta.iloc[1, 0]
        poste_cell = df_soft_meta.iloc[2, 0]

        nom_prenom = nom_prenom_cell.split(":", 1)[1].strip() if ":" in nom_prenom_cell else nom_prenom_cell.strip()
        poste = poste_cell.split(":", 1)[1].strip() if ":" in poste_cell else poste_cell.strip()

        nom_prenom = re.sub(r"\b(?:\d+|Na|nan|None)\b", "", nom_prenom).strip()
        poste = re.sub(r"\b(?:\d+|Na|nan|None)\b", "", poste).strip()

        parts = nom_prenom.split()
        prenom = parts[0] if parts else ""
        nom = " ".join(parts[1:]) if len(parts) > 1 else ""

        df_personnes = pd.DataFrame([{"Nom": nom, "Prénom": prenom, "Poste": poste}])

        df_soft_data = pd.read_excel(excel_file, sheet_name=feuille_soft, skiprows=5, header=0)

        df_soft_data_clean = df_soft_data.dropna(how='all')

        df_soft_level = pd.read_excel(excel_file, sheet_name=feuille_soft, skiprows=5, usecols=[1])

        return df_personnes, df_soft_data_clean, df_soft_level

    except Exception as e:
        print("❌ Erreur lors de la lecture du fichier Excel :", e)
        return None, None, None, None, None


# === Insertion des données ===
def inserer_donnees(df_personnes, df_soft_data_clean, df_soft_level):
    if any(x is None for x in (df_personnes, df_soft_data_clean, df_soft_level)):
        print("❌ Données non valides.")
        return

    conn = connexion_mysql()
    cursor =  conn.cursor(buffered=True)

    try:
        # Nettoyage
        #cursor.execute("DELETE FROM personne")
        #cursor.execute("DELETE FROM soft")
       # cursor.execute("DELETE FROM niveau_soft")

        # Insertion personne
        for _, row in df_personnes.iterrows():
            cursor.execute(
                "INSERT INTO personne (nom, prenom, poste) VALUES (%s, %s, %s)",
                (row["Nom"], row["Prénom"], row["Poste"])
            )
        cursor.execute("SELECT id FROM personne WHERE nom = %s AND prenom = %s", (row["Nom"], row["Prénom"]))
        id_personne = cursor.fetchone()[0]
        print(f"🧍 ID Personne: {id_personne}")

        # Appel des classes

        soft_inserter = soft_skills.SoftSkillInserter(cursor, conn, df_soft_data_clean, id_personne)
        soft_inserter.inserer()

        print("✅ Données insérées avec succès.")

    except Exception as e:
        print("❌ Erreur lors de l'insertion :", e)
        conn.rollback()

    finally:
        conn.close()

def run_person_only(fichier):
    df_personnes, *_ = lire_excel(fichier)
    if df_personnes is None:
        return None
    conn = connexion_mysql()
    cursor = conn.cursor()
    row = df_personnes.iloc[0]
    cursor.execute(
        "INSERT INTO personne (nom, prenom, poste, intercontrat) VALUES (%s, %s, %s, %s)",
        (row["Nom"], row["Prénom"], row["Poste"], 0)
    )
    id_personne = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_personne

# À la fin de import_excel_soft.py

def run_soft(id_personne, fichier):
    df_personnes, df_soft_data_clean, df_soft_level = lire_excel(fichier)

    if id_personne is None:
        print("❌ ID personne invalide.")
        return

    if df_soft_data_clean is None or df_soft_data_clean.empty:
        print("❌ Données soft invalides ou vides.")
        return

    conn = connexion_mysql()
    cursor =  conn.cursor(buffered=True)
    try:
        soft_inserter = soft_skills.SoftSkillInserter(cursor, conn, df_soft_data_clean, id_personne)
        soft_inserter.inserer()
        conn.commit()
        print(f"✅ Soft skills insérées pour ID {id_personne}")
    except Exception as e:
        print("❌ Erreur lors de l'insertion soft:", e)
        conn.rollback()
    finally:
        conn.close()




if __name__ == "__main__":
    dossier = "Matrices"
    for i in range(46, 90):
        fichier = os.path.join(dossier, f"{i}.xlsx")
        print(f"📄 Traitement de : {fichier}")
        df_personnes, df_soft_data_clean, df_soft_level = lire_excel(fichier)
        inserer_donnees(df_personnes, df_soft_data_clean, df_soft_level)
