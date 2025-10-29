import pickle
import os
from modules.Author import Author

class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.documents = {}
        self.id_document = 0
        self.authors = {}

    def add_document(self, document):
        """
        Ajoute un document au corpus et met à jour les auteurs
        """
        # Ajouter le document au dictionnaire
        self.documents[self.id_document] = document
        self.id_document += 1

        # Gérer l'auteur
        author_name = document.auteur
        if author_name not in self.authors:
            self.authors[author_name] = Author(name=author_name)

        # Ajouter le document à la production de l'auteur
        self.authors[author_name].add_author_doc(document)

    def __repr__(self):
        return (f"Corpus: {self.nom}\n"
                f"  - Nombre de documents: {len(self.documents)}\n"
                f"  - Nombre d'auteurs: {len(self.authors)}\n"
                f"  - ID du prochain document: {self.id_document}")



    def show_sorted_by_title(self):
        # Créer une liste de tuples (doc_id, document)
        docs_list = list(self.documents.items())

        # Trier par titre
        sorted_docs = sorted(docs_list, key=lambda x: x[1].titre.lower())

        # Afficher les résultats
        print(f"\n{'=' * 80}")
        print(f"Documents triés par titre ('A-Z')")
        print(f"Affichage de {len(sorted_docs)} document(s)")
        print(f"{'=' * 80}\n")

        for doc_id, doc in sorted_docs:
            print(f"[ID: {doc_id}]")
            print(f"Titre: {doc.titre}")
            print(f"Auteur: {doc.auteur}")
            print(f"Date: {doc.date}")
            print(f"Texte: {doc.texte[:100]}{'...' if len(doc.texte) > 100 else ''}")
            print(f"{'-' * 80}\n")

    def show_sorted_by_date(self, ascending=True):
        docs_list = list(self.documents.items())
        # Trier par date
        docs_list.sort(key=lambda x: x[1].date, reverse=not ascending)

        # Afficher les résultats
        print(f"\n{'='*80}")
        print(f"Documents triés par date ({'croissant' if ascending else 'décroissant'})")
        print(f"Affichage de {len(docs_list)} document(s)")
        print(f"{'='*80}\n")

        for doc_id, doc in docs_list:
            print(f"[ID: {doc_id}]")
            print(f"Titre: {doc.titre}")
            print(f"Auteur: {doc.auteur}")
            print(f"Texte: {doc.texte[:100]}{'...' if len(doc.texte) > 100 else ''}")
            print(f"{'-' * 80}\n")

    def save(self, directory='data'):
        """
        Sauvegarde le corpus sur le disque dur au format pickle
        """
        # Créer le dossier s'il n'existe pas
        os.makedirs(directory, exist_ok=True)
        filepath = f"{directory}/{self.nom}_corpus.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
            print(f"✅ Corpus sauvegardé en format pickle: {filepath}")

    def load(filepath):
        """
        Charge un corpus depuis le disque dur
        Retourne:
        - Un objet Corpus
        """

        with open(filepath, 'rb') as f:
            corpus = pickle.load(f)
            print(f"✅ Corpus chargé depuis: {filepath}")
        return corpus
