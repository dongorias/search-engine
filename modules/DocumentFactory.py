from modules.Document import Document, RedditDocument, ArxivDocument


class DocumentFactory:
    """
    Factory Pattern pour la création de documents.
    Permet de créer différents types de documents de manière centralisée.
    """

    @staticmethod
    def create_document(source, **kwargs):
        """
        Crée un document en fonction du type spécifié.

        Args:
            source (str): Type de document ('reddit', 'arxiv')
            **kwargs: Paramètres spécifiques au type de document

        Returns:
            Document: Instance du type de document approprié

        Raises:
            ValueError: Si le type de document n'est pas reconnu
        """
        doc_type = source.lower()

        if doc_type == 'reddit':
            return RedditDocument(**kwargs)
        elif doc_type == 'arxiv':
            return ArxivDocument(**kwargs)
        else:
            return Document(**kwargs)