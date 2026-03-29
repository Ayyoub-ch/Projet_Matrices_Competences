import pandas as pd
from sqlalchemy import create_engine
import mysql.connector
from flask import Flask, request, render_template

app = Flask(__name__)

#Classe Matrice
class Matrice:
    def __init__(self, host='localhost', user='root', password='', database='matrice',port=3306):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
        )
        self.cursor = self.conn.cursor()

    # Méthode pour insérer des données depuis un DataFrame
   # def insert_from_dataframe(self, df, table_name):
    #    engine = create_engine('mysql+pymysql://root:@localhost/matrice')
    #    df.to_sql(table_name, engine, if_exists='append', index=False)
    
    #Partie Personne
    def insert_personne(self, nom, prenom, poste):
        sql = "INSERT INTO personne (nom, prenom, poste) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (nom, prenom, poste))
        self.conn.commit()

    def update_personne_par_prenom(self, new_prenom, nom, poste):
        sql = "UPDATE personne SET nom = %s WHERE prenom = %s and poste = %s"
        self.cursor.execute(sql, (new_prenom, nom, poste))
        self.conn.commit()
    
    def update_personne_par_nom(self, new_nom, prenom):
        sql = "UPDATE personne SET prenom = %s WHERE nom = %s"
        self.cursor.execute(sql, (new_nom, prenom))
        self.conn.commit()
    
    def lecture_personne(self):
        self.cursor.execute("SELECT nom, prenom , poste FROM personne")
        return self.cursor.fetchall()
    
    def delete_personne(self, nom, prenom, poste):
        sql = "DELETE FROM personne WHERE nom = %s AND prenom = %s AND poste = %s"
        self.cursor.execute(sql, (nom, prenom, poste))
        self.conn.commit()
    
    def existe_personne(self, prenom, nom, poste):
        sql = "SELECT * FROM personne WHERE nom = %s AND prenom = %s AND poste = %s"
        self.cursor.execute(sql, (nom, prenom, poste))
        result = self.cursor.fetchone()
        return result is not None

    #Partie Soft Skill
    def insert_soft(self, competence2):
        sql = "INSERT INTO soft (competence2) VALUES (%s)"
        self.cursor.execute(sql, (competence2,))
        self.conn.commit()

    
    def update_soft(self, old_competence2, new_competence2):
        sql = "UPDATE soft SET competence2 = %s WHERE competence2 = %s"
        self.cursor.execute(sql, (new_competence2, old_competence2))
        self.conn.commit()
    

    def lecture_soft(self):
        self.cursor.execute("SELECT competence2 FROM soft")
        return self.cursor.fetchall()
    
    def delete_soft(self, competence2):
        sql = "DELETE FROM soft WHERE competence2 = %s"
        self.cursor.execute(sql, (competence2,))
        self.conn.commit()
    
    def existe_soft(self, competence2):
        sql = "SELECT * FROM soft WHERE competence2 = %s"
        self.cursor.execute(sql, (competence2,))
        result = self.cursor.fetchone()
        return result is not None


    #Partie Hard Skill
    def insert_hard(self, competence1, categorie):
        sql = "INSERT INTO hard (competence1, categorie) VALUES (%s, %s)"
        self.cursor.execute(sql, (competence1, categorie))
        self.conn.commit()

    def update_hard(self, competence1, new_categorie):
        sql = "UPDATE hard SET categorie = %s WHERE competence1 = %s"
        self.cursor.execute(sql, (new_categorie, competence1))
        self.conn.commit()


    
    def lecture_hard(self):
        self.cursor.execute("SELECT competence1, categorie FROM hard")
        return self.cursor.fetchall()

    def delete_hard(self, competence1, categorie):
        sql = "DELETE FROM hard WHERE competence1 = %s AND categorie = %s"
        self.cursor.execute(sql, (competence1, categorie))
        self.conn.commit()

    def existe_hard(self, competence1, categorie):
        sql = "SELECT * FROM hard WHERE competence1 = %s AND categorie = %s"
        self.cursor.execute(sql, (competence1, categorie))
        result = self.cursor.fetchone()
        return result is not None
    

    
@app.route('/')
def debut():
    return render_template('tableau.html')

# Insertion des données (POST)
@app.route('/insert', methods=['POST'])
def insert():
    nom = request.form['nom']
    prenom = request.form['prenom']
    poste = request.form['poste']
    competence1 = request.form['competence1']
    categorie = request.form['niveau']
    competence2 = request.form['competence2']

    conn = Matrice()
    conn.insert_soft(competence2)
    conn.insert_hard(competence1, categorie)
    conn.insert_personne(nom, prenom, poste)

    return render_template('tableau.html')

# Importation des données depuis un fichier Excel spécifique
@app.route('/import_excel', methods=['POST'])
def import_excel():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file:
        # Lire les feuilles spécifiques du fichier Excel
        df_soft = pd.read_excel(file, sheet_name="Matrice soft skills", engine='openpyxl')
        df_hard = pd.read_excel(file, sheet_name="Matrice hard skills", engine='openpyxl')

        # Insérer les données dans les tables correspondantes
        conn = Matrice()
        conn.insert_from_dataframe(df_soft[['competence2']], 'soft')
        conn.insert_from_dataframe(df_hard[['competence1', 'categorie']], 'hard')

        return "Data imported successfully", 200
    
@app.route('/check_data')
def check_data():
    conn = Matrice()
    personnes = conn.lecture_personne()
    hard_skills = conn.lecture_hard()
    soft_skills = conn.lecture_soft()

    print("PERSONNES:", personnes)
    print("HARD SKILLS:", hard_skills)
    print("SOFT SKILLS:", soft_skills)

    return render_template('check_data.html', personnes=personnes, hard_skills=hard_skills, soft_skills=soft_skills)



# Point d'entrée principal
if __name__ == '__main__':
    app.run(debug=True)