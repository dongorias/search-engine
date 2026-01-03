import pickle
import os
import re
import numpy as np
import pandas as pd
from modules.Author import Author
from modules.singleton import singleton


def nettoyer_texte(texte):
    """
    Nettoie un texte en appliquant plusieurs traitements.

    Args:
        texte: La chaîne de caractères à nettoyer

    Returns:
        Texte nettoyé
    """
    # Mise en minuscules
    texte = texte.lower()

    # Remplacer les passages à la ligne par des espaces
    texte = texte.replace('\n', ' ')
    texte = texte.replace('\r', ' ')
    texte = texte.replace('\t', ' ')

    # Remplacer les ponctuations par des espaces
    texte = re.sub(r'[^\w\s]', ' ', texte)

    # Remplacer les chiffres par des espaces
    texte = re.sub(r'\d+', ' ', texte)

    # Remplacer les espaces multiples par un seul espace
    texte = re.sub(r'\s+', ' ', texte)

    # Supprimer les espaces en début et fin
    texte = texte.strip()

    return texte


class Corpus:

    def __init__(self, nom):
        self.nom = nom
        self.documents = {}
        self.id_document = 0
        self.authors = {}
        self._full_text = None  # Cache pour le texte complet concaténé

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
        print(f"\n{'=' * 80}")
        print(f"Documents triés par date ({'croissant' if ascending else 'décroissant'})")
        print(f"Affichage de {len(docs_list)} document(s)")
        print(f"{'=' * 80}\n")

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

    def _get_full_text(self):
        """
        Construit et retourne le texte complet du corpus (avec cache).
        Cette méthode est appelée une seule fois lors du premier appel à search ou concorde.
        """
        if self._full_text is None:
            # Concaténer tous les textes des documents avec un séparateur
            texts = [doc.texte for doc in self.documents.values()]
            self._full_text = " ".join(texts)
        return self._full_text

    # def search(self, keyword):
    #     """
    #     Recherche les passages contenant le mot-clé dans le corpus.
    #
    #     Args:
    #         keyword: Le mot-clé à rechercher
    #
    #     Returns:
    #         Liste des passages contenant le mot-clé
    #     """
    #
    #     full_text = self._get_full_text()
    #
    #     match = re.finditer(keyword, full_text)
    #     return match

    def concorde(self, expression, context_size: int = 10)-> pd.DataFrame:
        """
        Construit un concordancier pour une expression donnée.

        Args:
            expression: L'expression à rechercher
            context_size: Taille du contexte (nombre de caractères) de chaque côté

        Returns:
            DataFrame pandas avec trois colonnes: contexte gauche, motif trouvé, contexte droit
        """

        full_text = self._get_full_text()

        # Pattern pour rechercher l'expression
        pattern = rf'{expression}'

        # Trouver toutes les occurrences
        matches = re.finditer(pattern, full_text, re.IGNORECASE)

        # Listes pour stocker les résultats
        contexte_gauche = []
        motif_trouve = []
        contexte_droit = []

        for match in matches:
            start = match.start()
            end = match.end()

            # Extraire le contexte gauche
            left_start = max(0, start - context_size)
            left_context = full_text[left_start:start]

            # Extraire le motif trouvé
            found_pattern = full_text[start:end]

            # Extraire le contexte droit
            right_end = min(len(full_text), end + context_size)
            right_context = full_text[end:right_end]

            # Ajouter aux listes
            contexte_gauche.append(left_context)
            motif_trouve.append(found_pattern)
            contexte_droit.append(right_context)

        # Créer le DataFrame
        df = pd.DataFrame({
            'contexte gauche': contexte_gauche,
            'motif trouvé': motif_trouve,
            'contexte droit': contexte_droit
        })

        return df

    def stats(self, n=10):
        """
          Affiche les statistiques textuelles sur le corpus.

          Args:
              n: Nombre de mots les plus fréquents à afficher (par défaut: 10)
          """
        # Dictionnaire pour compter les occurrences de chaque mot
        word_count = {}
        # Dictionnaire pour compter dans combien de documents apparaît chaque mot (document frequency)
        doc_frequency = {}
        # Ensemble de tous les mots du vocabulaire
        vocabulary = set()

        # Parcourir tous les documents
        for doc_ic, doc in self.documents.items():
            # Nettoyer le texte
            texte_nettoye = nettoyer_texte(doc.texte)

            # Séparer en mots
            mots = texte_nettoye.split()

            # Ensemble des mots uniques dans ce document (pour document frequency)
            mots_uniques_doc = set(mots)

            # Compter les occurrences et ajouter au vocabulaire
            for mot in mots:
                if mot:  # Ignorer les chaînes vides
                    vocabulary.add(mot)
                    #Recherche la clé mot dans le dictionnaire
                    #Si le mot existe : retourne sa valeur actuelle (nombre d'occurrences)
                    #Si le mot n'existe pas : retourne 0 (valeur par défaut)
                    #Ajoute 1 au compteur actuel
                    word_count[mot] = word_count.get(mot, 0) + 1

            # Mettre à jour la document frequency
            for mot in mots_uniques_doc:
                if mot:
                 doc_frequency[mot] = doc_frequency.get(mot, 0) + 1

        # Créer un DataFrame avec les statistiques
        freq_df = pd.DataFrame({
            'nombre_document': len(self.documents),
            'mot': list(word_count.keys()),
            'occurrences': list(word_count.values()),
            'document_frequency': [doc_frequency[mot] for mot in word_count.keys()]
        })

        # Trier par nombre d'occurrences décroissant
        freq_df = freq_df.sort_values('occurrences', ascending=False).reset_index(drop=True)

        # Afficher les statistiques
        print(f"\n{'=' * 80}")
        print(f"STATISTIQUES DU CORPUS '{self.nom}'")
        print(f"{'=' * 80}")
        print(f"\n📊 Nombre de documents: {len(self.documents)}")
        print(f"📚 Nombre de mots différents dans le corpus: {len(vocabulary)}")
        print(f"📝 Nombre total de mots: {sum(word_count.values())}")
        print(f"\n{'=' * 80}")
        print(f"🏆 TOP {n} MOTS LES PLUS FRÉQUENTS")
        print(f"{'=' * 80}\n")

        # Afficher les n mots les plus fréquents
        print(freq_df.head(n).to_string(index=True))

        print(f"\n{'=' * 80}\n")

        return freq_df

    def build_vocab(self):
        """
        Construit le vocabulaire à partir de tous les documents du corpus.

        Returns:
            dict: Vocabulaire avec structure {mot: {id, total_occurrences, nb_docs_containing}}
        """
        # Collecte tous les mots uniques
        #all_words = set()
        docs_words = {}
        word_counts = {}  # Pour compter total_occurrences

        for doc_id, document in self.documents.items():
            texte_nettoye = nettoyer_texte(document.texte)
            mots = texte_nettoye.split()
            # Filtrer les mots vides
            mots = [mot for mot in mots if mot]

            # Stocker les mots nettoyés pour ce document
            docs_words[doc_id] = mots

            # Mettre à jour la fréquence totale des occurrences pour chaque mot
            for mot in mots:
                word_counts[mot] = word_counts.get(mot, 0) + 1

            #all_words.update(mots)

        # Trie par ordre alphabétique
        sorted_words = sorted(word_counts.keys())

        vocab = {}
        # Crée le vocabulaire
        for idx, word in enumerate(sorted_words):
            vocab[word] = {
                'id': idx,
                'total_occurrences': word_counts[word],
                'nb_docs_containing': 0
            }

        # 2.2. Compter le nombre de documents contenant chaque mot (DF)
        for doc_id, mots in docs_words.items():
            # Utiliser un ensemble (set) pour ne compter le mot qu'une seule fois par document
            mots_uniques_doc = set(mots)
            for mot in mots_uniques_doc:
                if mot in vocab:
                    vocab[mot]['nb_docs_containing'] += 1

        print(f"      → {len(vocab)} mots uniques indexés.")


        return vocab

    @staticmethod
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
