from scipy.sparse import csr_matrix
import numpy as np
import pandas as pd
import math
from collections import Counter
from typing import List, Dict
from tqdm import tqdm
from modules.Corpus import nettoyer_texte


class SearchEngine:
    """
    Moteur de recherche basé sur une matrice Documents x Termes.
    Utilise les mesures TF et TF-IDF pour calculer la similarité entre une requête et les documents.
    """

    def __init__(self, corpus):
        """
        Initialise le moteur de recherche avec un corpus et construit la matrice Documents x Termes.

        Args:
            corpus: Objet de type Corpus contenant les documents à indexer
        """
        self.corpus = corpus
        self.vocab = {}
        self.mat_TF = None
        self.mat_TFIDF = None

        # Construction du vocabulaire et des matrices
        self._build_vocabulary()
        self._build_tf_matrix()
        self._compute_word_statistics()
        self._build_tfidf_matrix()

    def _tokenize(self, text: str) -> List[str]:
        """
        Découpe le texte en mots (tokens).

        Args:
            text: Texte à découper

        Returns:
            Liste de mots en minuscules
        """
        # Supprime la ponctuation et convertit en minuscules
        texte_nettoye = nettoyer_texte(text)
        mots = texte_nettoye.split()
        return [mot for mot in mots if mot]  # Filtrer les chaînes vides

    def _build_vocabulary(self):
        """
        Construit le dictionnaire de vocabulaire à partir de tous les documents du corpus.
        Le vocabulaire est trié par ordre alphabétique.
        """
        self.vocab = self.corpus.build_vocab()

    def _build_tf_matrix(self):
        # Dimensions de la matrice
        n_docs = len(self.corpus.documents)
        n_vocab = len(self.vocab)

        # Listes pour construire la matrice creuse (CSR)
        data, rows, cols = [], [], []
        print("      → Construction de la matrice TF...")
        for doc_idx, (doc_id, document) in tqdm(enumerate(self.corpus.documents.items()), total=n_docs, desc="Indexation"):
            words = self._tokenize(document.texte)
            word_counts = Counter(words)

            for word, count in word_counts.items():
                if word in self.vocab:
                    word_idx = self.vocab[word]['id']

                    # Stockage des valeurs (TF) et de leurs coordonnées
                    data.append(count)  # La valeur TF (fréquence brute)
                    rows.append(doc_idx)  # Indice du document (Ligne)
                    cols.append(word_idx)  # Indice du mot (Colonne)

        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(n_docs, n_vocab), dtype=np.float64)
        print(f"      → Matrice TF {n_docs} × {n_vocab} (creuse) construite.")

    def _build_tfidf_matrix(self):
        n_docs = len(self.corpus.documents)  # N (Nombre total de documents)
        n_vocab = len(self.vocab)  # Taille du vocabulaire
        self.idf = np.zeros(n_vocab)  # Initialise un tableau NumPy pour stocker les poids IDF

        # Parcourt le vocabulaire pour remplir le vecteur IDF
        for word, info in self.vocab.items():
            word_idx = info['id']
            df = info['nb_docs_containing']  # DF(t) : Fréquence documentaire

            # Le DF doit être supérieur à zéro pour éviter une division par zéro
            if df > 0:
                # Application de la formule de l'IDF : log(N / DF(t))
                self.idf[word_idx] = math.log(n_docs / df)

        # Convertir la matrice TF creuse en format dense (np.array) pour la multiplication vectorielle
        mat_tf_dense = self.mat_TF.toarray()

        # Multiplication du tableau 2D (TF) par le vecteur 1D (IDF).
        # ce qui applique le poids IDF à la fréquence TF correspondante.
        mat_tfidf_dense = mat_tf_dense * self.idf

        # Reconversion en matrice creuse pour optimiser l'espace et les calculs futurs.
        self.mat_TFIDF = csr_matrix(mat_tfidf_dense)

        print(f"      → Matrice TF-IDF {n_docs} × {n_vocab} (creuse).")
        print(f"      → IDF: min={self.idf.min():.4f}, max={self.idf.max():.4f}")

        return self.mat_TFIDF

    def _compute_word_statistics(self):
        """
        Calcule pour chaque mot:
        - Le nombre total d'occurrences dans le corpus
        - Le nombre de documents contenant ce mot
        """
        # Nombre total d'occurrences par mot (somme sur toutes les lignes)
        total_occurrences = np.array(self.mat_TF.sum(axis=0)).flatten()

        # Nombre de documents contenant chaque mot (compte les valeurs non nulles)
        nb_docs_containing = np.array((self.mat_TF > 0).sum(axis=0)).flatten()

        # Met à jour le vocabulaire
        for word, info in self.vocab.items():
            word_idx = info['id']
            info['total_occurrences'] = int(total_occurrences[word_idx])
            info['nb_docs_containing'] = int(nb_docs_containing[word_idx])


    def _query_to_vector(self, query: str) -> np.ndarray:
        """
        Transforme une requête en vecteur sur le vocabulaire.

        Args:
            query: Chaîne de caractères contenant les mots-clés de la requête

        Returns:
            Vecteur numpy de dimension N_vocab
        """
        #query_vector = np.zeros(len(self.vocab))
        n_vocab = len(self.vocab)
        query_vector_tfidf = np.zeros(n_vocab)
        words = self._tokenize(query)
        word_counts = Counter(words)

        # 3. Application de la pondération IDF (TF * IDF)
        for word, count in word_counts.items():
            if word in self.vocab:
                word_idx = self.vocab[word]['id']

                # Poids TF (Fréquence du terme dans la requête)
                tf_poids = count

                # Poids IDF (Inverse Document Frequency, précalculé sur le corpus)
                # self.idf doit être un attribut de votre classe
                idf_poids = self.idf[word_idx]

                # TF-IDF = TF * IDF
                query_vector_tfidf[word_idx] = tf_poids * idf_poids

        print(f"      → Requête vectorisée en {n_vocab} dimensions (TF-IDF).")

        return query_vector_tfidf

    def _cosine_similarity(self, query_vector: np.ndarray) -> np.ndarray:
        """
        Calcule la similarité cosinus entre le vecteur requête et tous les documents.

        Args:
            query_vector: Vecteur représentant la requête

        Returns:
            Vecteur de similarités de dimension N_docs
        """

        # Normalise le vecteur requête
        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:

            return np.zeros(self.mat_TFIDF.shape[0])

        query_normalized = query_vector / query_norm

        # Calcule le produit scalaire avec chaque document
        doc_vectors = self.mat_TFIDF.toarray()

        # Normalise les vecteurs documents
        doc_norms = np.linalg.norm(doc_vectors, axis=1)
        doc_norms[doc_norms == 0] = 1  # Évite la division par zéro

        doc_vectors_normalized = doc_vectors / doc_norms[:, np.newaxis]

        # Similarité cosinus = produit scalaire des vecteurs normalisés
        similarities = np.dot(doc_vectors_normalized, query_normalized)

        return similarities

    def search(self, query: str, n_results: int = 5) -> pd.DataFrame:
        """
        Recherche les documents les plus pertinents pour une requête donnée.

        Args:
            query: Mots-clés de la requête (chaîne de caractères)
            n_results: Nombre de documents à retourner

        Returns:
            DataFrame pandas contenant les résultats triés par pertinence
        """
        # Transforme la requête en vecteur
        query_vector = self._query_to_vector(query)

        # Calcule les similarités
        similarities = self._cosine_similarity(query_vector)

        # Trie les documents par similarité décroissante
        ranked_indices = np.argsort(similarities)[::-1]

        # Limite au nombre de résultats demandés
        top_indices = ranked_indices[:n_results]

        # Construit le DataFrame de résultats
        results = []
        for rank, doc_idx in tqdm(enumerate(top_indices, start=1), total=len(top_indices), desc="Récupération des résultats"):
            # Récupère le document correspondant
            doc_id = list(self.corpus.documents.keys())[doc_idx]
            document = self.corpus.documents[doc_id]

            # Extrait les informations pertinentes
            result = {
                'Rank': rank,
                'Document_ID': doc_id,
                'Score': similarities[doc_idx],
                'Title': document.titre,
                'Author': document.auteur,
                'Date': document.date,
                'Text_Preview': document.texte[:50] + '...' if len(document.texte) > 100 else document.texte
            }
            results.append(result)

        return pd.DataFrame(results)

    def get_vocabulary_stats(self) -> pd.DataFrame:
        """
        Retourne les statistiques sur le vocabulaire.

        Returns:
            DataFrame contenant les mots et leurs statistiques
        """
        vocab_data = []
        for word, info in sorted(self.vocab.items()):
            vocab_data.append({
                'Word': word,
                'ID': info['id'],
                'Total_Occurrences': info['total_occurrences'],
                'Nb_Docs': info['nb_docs_containing']
            })

        return pd.DataFrame(vocab_data)