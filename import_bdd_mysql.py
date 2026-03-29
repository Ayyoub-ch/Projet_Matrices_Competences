# import_bdd_mysql.py

import mysql.connector
import os
from datetime import datetime


def get_all_hard_competences():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT competence1 FROM hard ORDER BY competence1")
        result = cursor.fetchall()
        cursor.close()
        return result  # Liste de tuples : [(1, "Python"), (2, "SQL"), ...]
    finally:
        conn.close()




def get_personn(intercontrat=0):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )
    cursor = conn.cursor()

    if intercontrat== 1:
        cursor.execute("SELECT id, nom, prenom FROM personne WHERE intercontrat = 1")
    else:
        cursor.execute("SELECT id, nom, prenom FROM personne")

    personnes = cursor.fetchall()
    cursor.close()
    conn.close()
    return personnes



def get_comp(id_hard):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )

    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute("""SELECT hard.competence1, hard.categorie, niveau_hard.niveau
                        FROM hard
                        JOIN niveau_hard ON hard.id = niveau_hard.id_hard
                        WHERE niveau_hard.id_hard = %s""", (id_hard,))
        hard_skills = [
            {"competence1": row[0], "categorie": row[1], "niveau": row[2]} for row in cursor.fetchall()
        ]
        cursor.close()
        return hard_skills
    
    finally:
        conn.close()


def get_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )

    try:
        cursor = conn.cursor(buffered=True)

        # Personnes
        cursor.execute("SELECT nom, prenom, poste, id, intercontrat FROM personne")
        personnes = cursor.fetchall()
        id_personne=personnes[0][3]

        # Hard Skills
        cursor.execute("""SELECT hard.competence1, hard.categorie, niveau_hard.niveau
                        FROM hard
                        JOIN niveau_hard ON hard.id = niveau_hard.id_hard
                        WHERE niveau_hard.id_personne = %s""", (id_personne,))
        hard_skills = [
            {"competence1": row[0], "categorie": row[1], "niveau": row[2]} for row in cursor.fetchall()
        ]

        cursor.close()

        cursor = conn.cursor(buffered=True)

        # Soft Skills
        cursor.execute("""SELECT soft.competence2, niveau_soft.niveau
                        FROM soft
                        JOIN niveau_soft ON soft.id = niveau_soft.id_soft
                        WHERE niveau_soft.id_personne = %s""", (id_personne,))
        
        soft_skills = [
            {"competence2": row[0], "niveau": row[1]} for row in cursor.fetchall()
        ]
        
        cursor.close()

        
        return personnes, hard_skills, soft_skills

    finally:
        conn.close()

def recherche_avec_filtre(id_personne=None, competence=None):
    import mysql.connector
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )

    try:
        if id_personne is not None:
            # Recherche par personne
            cursor1 = conn.cursor(buffered=True)
            cursor1.execute("""
                SELECT 
                    personne.id,
                    personne.nom, 
                    personne.prenom, 
                    personne.poste,
                    personne.intercontrat,        
                    hard.competence1, 
                    hard.categorie, 
                    niveau_hard.niveau
                FROM personne
                JOIN niveau_hard ON personne.id = niveau_hard.id_personne
                JOIN hard ON niveau_hard.id_hard = hard.id
                WHERE personne.id = %s
            """, (id_personne,))
            hard_results = cursor1.fetchall()
            cursor1.close()

            cursor2 = conn.cursor(buffered=True)
            cursor2.execute("""
                SELECT DISTINCT
                    personne.id,
                    personne.nom, 
                    personne.prenom, 
                    personne.poste,
                    personne.intercontrat,  
                    soft.competence2, 
                    niveau_soft.niveau
                FROM personne
                JOIN niveau_soft ON personne.id = niveau_soft.id_personne
                JOIN soft ON niveau_soft.id_soft = soft.id
                WHERE personne.id = %s
            """, (id_personne,))
            soft_results = cursor2.fetchall()
            cursor2.close()

            return {'type': 'personne', 'hard': hard_results, 'soft': soft_results}

        elif competence is not None:
            # Recherche par compétence
            cursor3 = conn.cursor(buffered=True)
            cursor3.execute("""
                SELECT 
                    personne.id,
                    personne.nom,
                    personne.prenom,
                    personne.poste,
                    personne.intercontrat,
                    hard.competence1,
                    hard.categorie,
                    niveau_hard.niveau
                FROM niveau_hard
                JOIN hard ON niveau_hard.id_hard = hard.id
                JOIN personne ON niveau_hard.id_personne = personne.id
                WHERE hard.competence1 = %s
                ORDER BY personne.nom, personne.prenom
            """, (competence,))
            results = cursor3.fetchall()
            cursor3.close()
            return {'type': 'competence', 'results': results}

        else:
            return {'type': 'aucun', 'message': 'Aucun identifiant fourni'}

    finally:
        conn.close()

def maj_intercontrat():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )
    cursor0 = conn.cursor(buffered=True)
    cursor0.execute("SELECT id FROM personne")
    id_personne=cursor0.fetchall()

    cursor1 = conn.cursor(buffered=True)
    cursor1.execute("SELECT id FROM personne")
    intercontrat=cursor1.fetchall()

    cursor = conn.cursor(buffered=True)
    
    if intercontrat== 1:
        cursor.execute("UPDATE personne SET intercontrat = 0 WHERE id='%s';", (id_personne,))
    else:
        cursor.execute("UPDATE personne SET intercontrat = 1 WHERE id='%s';", (id_personne,))
    
    conn.close()


def texte_a_trou():
    # Connexion base de données
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )
    cursor = conn.cursor(buffered=True)

    # Récupération des données
    cursor.execute("SELECT id FROM personne")
    liste_personne=cursor.fetchall()
    for row in liste_personne:
        id = row[0]
        cursor.execute("SELECT nom, prenom, poste, intercontrat FROM personne WHERE id = %s", (id,))
        personne = cursor.fetchone()  # (nom, prenom, poste)
        print(id)
        cursor.execute("""
            SELECT hard.competence1, hard.categorie, niveau_hard.niveau
            FROM hard
            JOIN niveau_hard ON hard.id = niveau_hard.id_hard
            WHERE niveau_hard.id_personne = %s
        """, (id,))
        hard_skills = cursor.fetchall()  # liste de tuples

        cursor.execute("""
            SELECT soft.competence2, niveau_soft.niveau
            FROM soft
            JOIN niveau_soft ON soft.id = niveau_soft.id_soft
            WHERE niveau_soft.id_personne = %s
        """, (id,))
        soft_skills = cursor.fetchall()


        if personne[3]==1:
            dispo="oui"
        else:
            dispo="non"

        texte_export = (
            f"Matrice \n"
            f"Civilité : \n{personne[0]} {personne[1]} - {personne[2]}\n"
            f"Disponibilité : \n{dispo}\n"
            f"Soft Skills : \n"
        )    

        for comp, niveau in soft_skills:
            texte_export += f"- {comp} (niveau:{niveau}); \n"

        texte_export += "\nHard Skills : \n"

        for comp, cat, niveau in hard_skills:
            texte_export += f"- {comp}  (niveau:{niveau}); \n"

        #texte_export += "\nParcours : \n"

        print(texte_export)

        # Création d'un dossier pour stocker les fichiers
        # Exemple : "exports/texte_1325_20250610"
        # Chemin absolu ou relatif vers le dossier souhaité
        dossier_path = os.path.expanduser("~/Documents/dossier_chatbot")

        # Créer le dossier s'il n'existe pas
        os.makedirs(dossier_path, exist_ok=True)

        # Générer le fichier texte dans ce dossier
        fichier_path = os.path.join(dossier_path, f"{personne[0]} {personne[1]}.txt")

        # Convertir texte_export (qui est une suite de tuples) en texte simple
        texte_final = texte_export

        # Écriture dans le fichier
        with open(fichier_path, "w", encoding="utf-8") as f_out:
            f_out.write(texte_final)

    conn.close()

    print(f"Fichier exporté dans : {fichier_path}")


def mapping():
    import mysql.connector

    # Connexion aux deux bases
    conn_cvtech = mysql.connector.connect(
        host="localhost", user="root", password="", database="cvtech"
    )
    cursor_cvtech = conn_cvtech.cursor(buffered=True)

    conn_matrice = mysql.connector.connect(
        host="localhost", user="root", password="", database="matrice"
    )
    cursor_matrice = conn_matrice.cursor(buffered=True)

    # --- Import des utilisateurs ---
    cursor_matrice.execute("SELECT id, nom, prenom, poste, intercontrat FROM personne;")
    personnes = cursor_matrice.fetchall()

    for id, nom, prenom, poste, intercontrat in personnes:
        last_name = nom.lower()
        first_name = prenom.lower()
        mail = last_name[0] + first_name + "@logical-conseils.com"
        password = "logical"
        roles = poste
        on_mission = intercontrat

        print(f"Insertion de : {mail}")
        try:
            cursor_cvtech.execute("""
                INSERT INTO users (id, last_name, first_name, mail, password, roles, on_mission)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id, nom, prenom, mail, password, roles, on_mission))
        except mysql.connector.Error as e:
            print(f"Erreur d'insertion user : {e}")

    # --- Import des compétences SOFT ---
    cursor_matrice.execute("""
        SELECT niveau_soft.id_personne, soft.competence2, niveau_soft.niveau 
        FROM niveau_soft
        JOIN soft ON niveau_soft.id_soft = soft.id
    """)
    soft = cursor_matrice.fetchall()

    # S'assurer que la catégorie "Soft Skills" existe
    cursor_cvtech.execute("SELECT id FROM skill_categories WHERE name = %s", ("Soft Skills",))
    result = cursor_cvtech.fetchone()
    id_cat_soft = result[0] if result else None

    if not id_cat_soft:
        cursor_cvtech.execute("INSERT INTO skill_categories (name) VALUES (%s)", ("Soft Skills",))
        id_cat_soft = cursor_cvtech.lastrowid

    print("Insertion des soft skills...")
    for id_user, competence2, niveau in soft:
        # Vérifier si la compétence existe déjà
        cursor_cvtech.execute("SELECT id FROM skills WHERE name = %s", (competence2,))
        skill = cursor_cvtech.fetchone()
        niveau=niveau

        if niveau=="Non Acquis":
            niveau=0
        else:
            niveau=1
            
        if skill:
            id_skill = skill[0]
        else:
            cursor_cvtech.execute(
                "INSERT INTO skills (id_skill_category, name) VALUES (%s, %s)",
                (id_cat_soft, competence2)
            )
            id_skill = cursor_cvtech.lastrowid

        # Associer à l'utilisateur si ce n'est pas déjà fait
        try:
            cursor_cvtech.execute(
                "INSERT INTO user_skills (id_user, id_skill, level) VALUES (%s, %s, %s)",
                (id_user, id_skill, niveau)
            )
            print(f"[SOFT] id_user: {id_user}, id_skill: {id_skill}, level: {niveau}")
            
        except mysql.connector.Error as e:
            print(f"Erreur d'association soft skill (user {id_user}, skill {id_skill}): {e}")

    # --- Import des compétences HARD ---
    cursor_matrice.execute("""
        SELECT niveau_hard.id_personne, hard.competence1, hard.categorie, niveau_hard.niveau 
        FROM niveau_hard
        JOIN hard ON niveau_hard.id_hard = hard.id
    """)
    hard = cursor_matrice.fetchall()

    print("Insertion des hard skills...")
    for id_user, competence1, categorie, niveau in hard:
        # S'assurer que la catégorie existe
        cursor_cvtech.execute("SELECT id FROM skill_categories WHERE name = %s", (categorie,))
        cat = cursor_cvtech.fetchone()
        id_cat_hard = cat[0] if cat else None
        niveau=niveau

        if not id_cat_hard:
            cursor_cvtech.execute("INSERT INTO skill_categories (name) VALUES (%s)", (categorie,))
            id_cat_hard = cursor_cvtech.lastrowid

        # Vérifier si la compétence existe
        cursor_cvtech.execute("SELECT id FROM skills WHERE name = %s", (competence1,))
        skill = cursor_cvtech.fetchone()

        if skill:
            id_skill = skill[0]
        else:
            cursor_cvtech.execute(
                "INSERT INTO skills (id_skill_category, name) VALUES (%s, %s)",
                (id_cat_hard, competence1)
            )
            id_skill = cursor_cvtech.lastrowid

        # Associer à l'utilisateur si ce n'est pas déjà fait
        try:
            cursor_cvtech.execute(
                "INSERT INTO user_skills (id_user, id_skill, level) VALUES (%s, %s, %s)",
                (id_user, id_skill, niveau)
            )
            print(f"[HARD] id_user: {id_user}, id_skill: {id_skill}, level: {niveau}")

        except mysql.connector.Error as e:
            print(f"Erreur d'association hard skill (user {id_user}, skill {id_skill}): {e}")

    # Finalisation
    print("Soft skills récupérées :", len(soft))
    print("Hard skills récupérées :", len(hard))
    conn_cvtech.commit()
    conn_matrice.commit()
    print("Migration terminée.")

    cursor_cvtech.close()
    conn_cvtech.close()
    cursor_matrice.close()
    conn_matrice.close()


