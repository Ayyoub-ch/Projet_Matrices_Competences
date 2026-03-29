import import_excel_soft
import import_excel_hard
import mysql.connector
import os

def connexion_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )

def run():
    conn = connexion_mysql()
    cursor = conn.cursor()

    try:
        # Nettoyage global
         #cursor.execute("DELETE FROM niveau_soft")
         #cursor.execute("DELETE FROM soft")
         #cursor.execute("DELETE FROM niveau_hard")
         #cursor.execute("DELETE FROM hard")
         #cursor.execute("DELETE FROM personne")

        conn.commit()
        conn.close()

        # Appels
        dossier = "Matrices"
        for i in range(46, 90):
            fichier = os.path.join(dossier, f"{i}.xlsx")
            print(f"📄 Traitement de : {fichier}")
            id_personne = import_excel_soft.run_person_only(fichier)
            import_excel_soft.run_soft(id_personne, fichier)
            import_excel_hard.run_hard(id_personne, fichier)

        print("✅ Import global terminé")

    except Exception as e:
        print("❌ Erreur globale :", e)
        conn.rollback()
        conn.close()
