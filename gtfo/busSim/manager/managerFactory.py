class ManagerFactory:
    def __init__(self):
        self._managers = {}

    def register_manager(self, key, manager):
        self._managers[key] = manager

    def create(self, key, **kwargs):
        manager = self._managers.get(key)
        if not manager:
            raise ValueError(key)
        return manager(**kwargs)
