from abc import ABC, abstractmethod
from pydantic import BaseModel


class CommandHandler(ABC):

    def __init__(self, data):
        self.data = data

    
    

