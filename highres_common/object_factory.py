# source: https://realpython.com/factory-method-python/
class ObjectFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        """
        The `register_builder` function adds a builder object to a dictionary with a specified key.

        :param key: The `key` parameter in the `register_builder` method is used as a unique identifier for
        the builder that is being registered. It is typically a string or any other hashable object that can
        be used as a key in a dictionary to store and retrieve the corresponding builder object
        :param builder: The `register_builder` method is used to register a builder function with a specific
        key in the `_builders` dictionary. The `key` parameter is the identifier for the builder function,
        and the `builder` parameter is the actual function that will be stored in the dictionary under that
        key
        """
        self._builders[key] = builder

    def create(self, key, **kwargs):
        """
        The `create` function takes a key and keyword arguments, retrieves a builder based on the key, and
        returns the result of calling the builder with the provided arguments.

        :param key: The `key` parameter in the `create` method is used to determine which builder function
        to use for creating an object. It is used to look up the appropriate builder function from the
        `_builders` dictionary based on the provided key
        :return: The `create` method returns the result of calling the builder function associated with the
        given key, passing in the keyword arguments `kwargs`.
        """
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)
