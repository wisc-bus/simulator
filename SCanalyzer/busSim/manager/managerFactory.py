import traceback

class ManagerFactory:
    def __init__(self):
        print('manger init')
#         for line in traceback.format_stack():
#             print(line.strip())
        self._managers = {}

    def register_manager(self, key, manager):
        print('mangager register')
#         for line in traceback.format_stack():
#             print(line.strip())
        self._managers[key] = manager

    def get_available_managers(self):
        print('get available manager')
#         for line in traceback.format_stack():
#             print(line.strip())
        return list(self._managers.keys())

    def create(self, key, **kwargs):
        print('manager create')
#         for line in traceback.format_stack():
#             print(line.strip())
        print(f'{self=}')
        print(f'{key=}')
        manager = self._managers.get(key)
        print(f'{manager=}')
        if not manager:
            raise ValueError(key)
        return manager(**kwargs)