

class InvalidRdbFileException(Exception):
    
    def __init__(self, header: str) -> None:

        self.message = f"File is not in RDB format -- Header was {header}"
        super().__init__(self.message)

class DynamicMethodNotFoundException(Exception):
    
    def __init__(self, obj, method_called: str) -> None:

        self.message = f"Method {method_called} not present in class {type(obj)}"
        super().__init__(self.message)

class ReplConfException(Exception):
    
    def __init__(self) -> None:

        self.message = "Replica configuration message unrecognized"
        super().__init__(self.message)


    



