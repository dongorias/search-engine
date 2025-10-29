def singleton(cls):
    """
    Décorateur Singleton qui garantit qu'une seule instance de la classe existe.
    """
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
            print(f"🔒 Singleton: Nouvelle instance de {cls.__name__} créée")
        else:
            print(f"🔒 Singleton: Instance existante de {cls.__name__} retournée")
        return instances[cls]

    return wrapper