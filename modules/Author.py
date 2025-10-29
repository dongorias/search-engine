class Author:
    def __init__(self,
                 name: str
                 ):
        self.name = name
        self.nb_docs = 0
        self.production = {}

    def add_author_doc(self, doc):
        self.production[self.nb_docs] = doc
        self.nb_docs += 1

    def __str__(self):
        return f" Author(name={self.name}, nb_docs={self.nb_docs}, production={self.production})"
