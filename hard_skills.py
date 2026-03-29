class HardSkillInserter:
    def __init__(self, cursor, conn, df_hard_clean, id_personne):
        self.cursor = cursor
        self.conn = conn
        self.df = df_hard_clean
        self.id_personne = id_personne

    def inserer(self):
        for _, row in self.df.iterrows():
            self.cursor.execute(
                "INSERT INTO hard (competence1, categorie) VALUES (%s, %s)",
                (row["Hard Skills / outils"], row["Catégorie"])
            )
            self.cursor.execute(
                "SELECT id FROM hard WHERE competence1 = %s",
                (row["Hard Skills / outils"],)
            )
            id_hard = self.cursor.fetchone()[0]
            print(f"✅ Hard ID: {id_hard}")

            if row["Niveau"] > 0:
                self.cursor.execute(
                    "INSERT INTO niveau_hard (id_personne, id_hard, niveau) VALUES (%s, %s, %s)",
                    (self.id_personne, id_hard, row["Niveau"])
                )
        self.conn.commit()