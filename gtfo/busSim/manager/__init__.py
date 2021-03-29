from .managerFactory import *
from .localManager import *
from .AWSManager import *

managerFactory = ManagerFactory()
managerFactory.register_manager("local", LocalManager)
managerFactory.register_manager("aws", AWSManager)
