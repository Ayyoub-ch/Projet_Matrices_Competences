class SoftSkillInserter:
    def __init__(self, cursor, conn, df_soft_data_clean, id_personne):
        self.cursor = cursor
        self.conn = conn
        self.df = df_soft_data_clean
        self.id_personne = id_personne

        # Renommage de la colonne du niveau si nécessaire
        if "." in self.df.columns:
            self.df.rename(columns={".": "Niveau"}, inplace=True)

    def inserer(self):
        for _, row in self.df.iterrows():
            self.cursor.execute(
                "INSERT INTO soft (competence2) VALUES (%s)",
                (row["Soft Skills"],)
            )
            self.cursor.execute(
                "SELECT id FROM soft WHERE competence2 = %s",
                (row["Soft Skills"],)
            )
            id_soft = self.cursor.fetchone()[0]
            print(f"✅ Soft ID: {id_soft}")

            self.cursor.execute(
                    "INSERT INTO niveau_soft (id_personne, id_soft, niveau) VALUES (%s, %s, %s)",
                    (self.id_personne, id_soft, row["Niveau"])
                )
        self.conn.commit()