from flask import Flask, render_template, abort, redirect, url_for, request, flash, abort
from import_bdd_mysql import get_data, get_personn, recherche_avec_filtre,get_comp, get_all_hard_competences, texte_a_trou, mapping
import import_excel_all
from import_bdd_mysql import texte_a_trou
import mysql.connector

app = Flask(__name__)

@app.route("/")
def index():
    try:
        personne=get_personn()
        return render_template(
            "admin.html",personne=personne
        )
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        abort(500, description="An error occurred while fetching data from the database.")

@app.route('/importer', methods=['POST'])
def importer_matrice():
    try:
        import_excel_all.run()  # ta fonction d'import
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Erreur lors de l'importation : {e}")
        abort(500, description="Erreur lors de l'importation des matrices.")


"""
@app.route('/voir_comp', methods=['POST'])
def voir_comp():
    try:
        personnes, hard_skills, soft_skills = get_data()
        return render_template(
            "tableaux.html",
            personnes=personnes,
            hard_skills=hard_skills,
            soft_skills=soft_skills)
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        abort(500, description="An error occurred while fetching data from the database.")
"""
@app.route('/retour', methods=['POST'])
def retour():
    return render_template("admin.html")


@app.route('/rechercher', methods=['POST'])
def rechercher():
    choix_personne = request.form.get("choix_personne")
    choix_competence = request.form.get("choix_competence")
    filtre_intercontrat = 1 if 'intercontrat' in request.form else 0

    print("Choix personne reçu :", repr(choix_personne))
    print("Choix compétence reçu :", repr(choix_competence))
    print("Intercontrat cochée :", filtre_intercontrat)

    personnes = get_personn(intercontrat=filtre_intercontrat)
    liste_competences = get_all_hard_competences()

    if not choix_personne and not choix_competence:
        return render_template(
            "recherche.html",
            personnes=personnes,
            hard_results=[],
            soft_results=[],
            choix_personne="",
            choix_competence="",
            filtre_intercontrat=filtre_intercontrat,
            liste_competences=liste_competences
        )

    try:
        if choix_personne:
            id_personne = int(choix_personne)
            results = recherche_avec_filtre(id_personne=id_personne)

            return render_template(
                "recherche.html",
                personnes=personnes,
                hard_results=results.get("hard", []),
                soft_results=results.get("soft", []),
                choix_personne=choix_personne,
                choix_competence="",
                filtre_intercontrat=filtre_intercontrat,
                liste_competences=liste_competences
            )

        elif choix_competence:
            results = recherche_avec_filtre(competence=choix_competence)
            hard_skills = get_comp(choix_competence)

            hard_results = results.get("results", [])

            if filtre_intercontrat == 1:
                hard_results = [res for res in hard_results if res[4] == 1]  # col 4 = intercontrat

            return render_template(
                "recherche.html",
                personnes=personnes,
                hard_results=hard_results,
                soft_results=[],  # pas de soft dans ce cas
                choix_personne="",
                choix_competence=choix_competence,
                filtre_intercontrat=filtre_intercontrat,
                hard_skills=hard_skills,
                liste_competences=liste_competences
            )

    except (ValueError, TypeError):
        # Cas où l'ID n'est pas un entier valide
        return render_template(
            "recherche.html",
            personnes=personnes,
            hard_results=[],
            soft_results=[],
            choix_personne=choix_personne,
            choix_competence=choix_competence,
            filtre_intercontrat=filtre_intercontrat,
            liste_competences=liste_competences
        )

    # Fallback
    return render_template(
        "recherche.html",
        personnes=personnes,
        hard_results=[],
        soft_results=[],
        choix_personne="",
        choix_competence="",
        filtre_intercontrat=filtre_intercontrat,
        liste_competences=liste_competences
    )


@app.route('/ecrire', methods=['POST'])
def ecrire_cv():      
    texte_a_trou()
    return redirect(url_for('index'))


@app.route('/cvtech', methods=['POST'])
def mapping_cvtech():      
    mapping()
    return redirect(url_for('index'))



@app.route('/maj_intercontrat', methods=['POST'])
def maj_intercontrat():
    id_personne = request.form.get('id_personne')
    intercontrat_val = 1 if request.form.get('intercontrat_personne') == '1' else 0

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )
    cursor = conn.cursor()
    cursor.execute("UPDATE personne SET intercontrat = %s WHERE id = %s", (intercontrat_val, id_personne))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('index'))  # Redirige vers la page d’administration ou la page souhaitée


@app.route('/reinitialiser_bdd', methods=['POST'])
def reinitialiser_bdd():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matrice"
    )

    try:
        cursor = conn.cursor()

        # Ordre explicite demandé pour réinitialiser les compteurs et vider les tables.
        cursor.execute("ALTER TABLE personne AUTO_INCREMENT=0;")
        cursor.execute("ALTER TABLE soft AUTO_INCREMENT=0;")
        cursor.execute("ALTER TABLE hard AUTO_INCREMENT=0;")
        cursor.execute("ALTER TABLE niveau_hard AUTO_INCREMENT=0;")
        cursor.execute("ALTER TABLE niveau_soft AUTO_INCREMENT=0;")
        cursor.execute("DELETE FROM niveau_soft;")
        cursor.execute("DELETE FROM soft;")
        cursor.execute("DELETE FROM niveau_hard;")
        cursor.execute("DELETE FROM hard;")
        cursor.execute("DELETE FROM personne;")

        conn.commit()
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erreur lors de la réinitialisation de la base : {e}")
        abort(500, description="Erreur lors de la réinitialisation de la base de données.")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))



"""
@app.route('/filtrage', methods=['GET', 'POST'])
def filtrer():
    categories = get_all_categories()

    if request.method == 'POST':
        selected = request.form.getlist('categories')
        filtered_skills = get_filtered_skills(selected)
    else:
        filtered_skills = get_filtered_skills()

    return render_template('recherche.html', categories=categories, filtered_skills=filtered_skills)


"""



if __name__ == "__main__":
    app.run(debug=True)
