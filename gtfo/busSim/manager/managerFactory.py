class ManagerFactory:
    def __init__(self):
        self._managers = {}

    def register_manager(self, key, manager):
        self._managers[key] = manager

    def get_available_managers(self):
        return list(self._managers.keys())

    def create(self, key, **kwargs):
        manager = self._managers.get(key)
        if not manager:
            raise ValueError(key)
        return manager(**kwargs)
