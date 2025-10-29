from datetime import datetime


class Document:
    def __init__(self,
                 titre, auteur, date: datetime, url, texte
                 ):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte

    def __str__(self):
        return f"Document(titre={self.titre}, auteur={self.auteur}, date={self.date}, url={self.url}, texte={self.texte[:50]}...)"

    def __repr__(self):
        """
        Représentation plus lisible du document
        """
        # Formater la date
        if isinstance(self.date, str):
            try:
                date_float = float(self.date)
                date_display = datetime.fromtimestamp(date_float).strftime('%Y-%m-%d')
            except:
                date_display = self.date
        elif isinstance(self.date, datetime):
            date_display = self.date.strftime('%Y-%m-%d')
        else:
            date_display = str(self.date)

        return (f"\n📄 Document:\n"
                f"  Titre: {self.titre}\n"
                f"  Auteur: {self.auteur}\n"
                f"  Date: {date_display}\n"
                f"  URL: {self.url}\n"
                f"  Longueur: {len(self.texte)} caractères\n"
                f"  Aperçu: {self.texte[:100]}...")

    # Getters
    def get_titre(self):
        return self.titre

    def get_auteur(self):
        return self.auteur

    def get_date(self):
        return self.date

    def get_url(self):
        return self.url

    def get_texte(self):
        return self.texte

    # Setters
    def set_titre(self, titre):
        self.titre = titre

    def set_auteur(self, auteur):
        self.auteur = auteur

    def set_date(self, date):
        self.date = date

    def set_url(self, url):
        self.url = url

    def set_texte(self, texte):
        self.texte = texte



# ============================================================================
# Classe RedditDocument - Hérite de Document
# ============================================================================

class RedditDocument(Document):
    """
    Classe représentant un document provenant de Reddit.
    Hérite de Document et ajoute des attributs spécifiques à Reddit.
    """

    def __init__(self,
                 titre,
                 auteur,
                 date: datetime,
                 url,
                 texte,
                 num_comments: int = 0,
                 score: int = 0,
                 subreddit: str = ""):
        """
        Constructeur de RedditDocument

        Args:
            titre: Titre du post Reddit
            auteur: Nom de l'auteur
            date: Date de publication
            url: URL du post
            texte: Contenu textuel du post
            num_comments: Nombre de commentaires
            score: Score (upvotes - downvotes)
            subreddit: Nom du subreddit
        """
        # Appel du constructeur de la classe mère
        super().__init__(titre, auteur, date, url, texte)

        # Attributs spécifiques à Reddit
        self.num_comments = num_comments
        self.score = score
        self.subreddit = subreddit
        self.source = "Reddit"

    # Getters
    def get_num_comments(self):
        """Retourne le nombre de commentaires"""
        return self.num_comments

    def get_score(self):
        """Retourne le score du post"""
        return self.score

    def get_subreddit(self):
        """Retourne le nom du subreddit"""
        return self.subreddit

    # Setters
    def set_num_comments(self, num_comments: int):
        """Définit le nombre de commentaires"""
        if num_comments >= 0:
            self.num_comments = num_comments
        else:
            raise ValueError("Le nombre de commentaires ne peut pas être négatif")

    def set_score(self, score: int):
        """Définit le score du post"""
        self.score = score

    def set_subreddit(self, subreddit: str):
        """Définit le nom du subreddit"""
        self.subreddit = subreddit

    # Méthode d'affichage spécifique
    def __str__(self):
        """
        Méthode d'affichage personnalisée pour RedditDocument
        """

        date_display = self.date.strftime('%Y-%m-%d %H:%M:%S')

        return (f"RedditDocument(\n"
                f"  📝 Titre: {self.titre}\n"
                f"  👤 Auteur: {self.auteur}\n"
                f"  📅 Date: {date_display}\n"
                f"  🔗 URL: {self.url}\n"
                f"  💬 Commentaires: {self._num_comments}\n"
                f"  ⬆️ Score: {self._score}\n"
                f"  📂 Subreddit: r/{self._subreddit}\n"
                f"  📄 Texte: {self.texte[:100]}{'...' if len(self.texte) > 100 else ''}\n"
                f")")

    def get_type(self):
        """Retourne le type de document"""
        return self.source



# ============================================================================
# Classe ArxivDocument - Hérite de Document
# ============================================================================


class ArxivDocument(Document):
    """
    Classe représentant un document provenant d'Arxiv.
    Hérite de Document et ajoute des attributs spécifiques à Arxiv.
    """

    def __init__(self,
                 titre,
                 auteur,
                 date: datetime,
                 url,
                 texte,
                 co_auteurs: list = None,
                 categories: list = None,
                 arxiv_id: str = ""):
        """
        Constructeur de ArxivDocument

        Args:
            titre: Titre de l'article
            auteur: Auteur principal
            date: Date de publication
            url: URL de l'article
            texte: Résumé de l'article
            co_auteurs: Liste des co-auteurs
            categories: Liste des catégories Arxiv
            arxiv_id: Identifiant Arxiv
        """
        # Appel du constructeur de la classe mère
        super().__init__(titre, auteur, date, url, texte)

        # Attributs spécifiques à Arxiv
        self.co_auteurs = co_auteurs if co_auteurs is not None else []
        self.categories = categories if categories is not None else []
        self.arxiv_id = arxiv_id
        self.source = "Arxiv"

    # Getters
    def get_co_auteurs(self):
        """Retourne la liste des co-auteurs"""
        return self.co_auteurs

    def get_all_auteurs(self):
        """Retourne tous les auteurs (principal + co-auteurs)"""
        return [self.auteur] + self.co_auteurs

    def get_categories(self):
        """Retourne la liste des catégories"""
        return self.categories

    def get_arxiv_id(self):
        """Retourne l'identifiant Arxiv"""
        return self.arxiv_id

    def get_nb_auteurs(self):
        """Retourne le nombre total d'auteurs"""
        return 1 + len(self.co_auteurs)

    # Setters
    def set_co_auteurs(self, co_auteurs: list):
        """Définit la liste des co-auteurs"""
        if isinstance(co_auteurs, list):
            self.co_auteurs = co_auteurs
        else:
            raise TypeError("co_auteurs doit être une liste")

    def add_co_auteur(self, co_auteur: str):
        """Ajoute un co-auteur à la liste"""
        if co_auteur not in self.co_auteurs:
            self.co_auteurs.append(co_auteur)

    def set_categories(self, categories: list):
        """Définit la liste des catégories"""
        if isinstance(categories, list):
            self.categories = categories
        else:
            raise TypeError("categories doit être une liste")

    def add_category(self, category: str):
        """Ajoute une catégorie à la liste"""
        if category not in self.categories:
            self.categories.append(category)

    def set_arxiv_id(self, arxiv_id: str):
        """Définit l'identifiant Arxiv"""
        self.arxiv_id = arxiv_id

    # Méthode d'affichage spécifique
    def __str__(self):
        """
        Méthode d'affichage personnalisée pour ArxivDocument
        """
        # Formater la date pour l'affichage
        if isinstance(self.date, datetime):
            date_display = self.date.strftime('%Y-%m-%d')
        else:
            date_display = str(self.date)

        # Formater la liste des auteurs
        if self.co_auteurs:
            auteurs_display = f"{self.auteur} et al. ({self.get_nb_auteurs()} auteurs)"
            co_auteurs_str = ", ".join(self.co_auteurs[:3])
            if len(self.co_auteurs) > 3:
                co_auteurs_str += f" et {len(self.co_auteurs) - 3} autre(s)"
        else:
            auteurs_display = self.auteur
            co_auteurs_str = "Aucun"

        # Formater les catégories
        categories_str = ", ".join(self.categories) if self.categories else "Non spécifiées"

        return (f"ArxivDocument(\n"
                f"  📝 Titre: {self.titre}\n"
                f"  👤 Auteur(s): {auteurs_display}\n"
                f"  👥 Co-auteurs: {co_auteurs_str}\n"
                f"  📅 Date: {date_display}\n"
                f"  🔗 URL: {self.url}\n"
                f"  🔢 ID Arxiv: {self.arxiv_id}\n"
                f"  🏷️ Catégories: {categories_str}\n"
                f"  📄 Résumé: {self.texte[:100]}{'...' if len(self.texte) > 100 else ''}\n"
                f")")


def __repr__(self):
    """
    Représentation détaillée pour le debugging
    """
    return (f"ArxivDocument(titre='{self.titre[:30]}...', "
            f"auteur='{self.auteur}', "
            f"nb_auteurs={self.get_nb_auteurs()}, "
            f"arxiv_id='{self._arxiv_id}')")


def get_type(self):
    """Retourne le type de document"""
    return self.source