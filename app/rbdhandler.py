import re
from typing import List
import argparse
from errorhandler.exceptions import InvalidRdbFileException, DynamicMethodNotFoundException

class RdbHandler:

    subsection_types_set: set = set(["FA","FB","FC","FD","FE","FF"])
    subsections_values_dict: dict = {subsection for subsection in subsection_types_set}
    file_byte_data: bytes
    position_in_file: int = 0
    

    def read_bits(self, byte_array: bytearray):
        """Reads bits from a byte, from most significant to least significant."""
        BYTE_SIZE = 8
        
        for byte in byte_array:
            for i in range(BYTE_SIZE):
                yield (byte >> (7 - i)) & 1


    def setrbd(self, parse_obj: argparse) -> None:
        
        args= parse_obj.parse_args()

        self.dir = args.dir
        self.file = args.dbfilename

        pass

    def rdb_file_parser(self, file_data) -> List[str]:
        
        version = self.valid_file(file_data)
        
        print("RDB version  number ", version)

        self.split_subsections(file_data[10:])

    
    def filehandler(self, obj, regex) -> None:

        print(regex)
        
        fpath = f'{obj.dir}/{obj.file}'
        print(fpath)

        try:
            with open(fpath, 'rb') as f:
               
               self.file_byte_data = f.read()
               
               value = self.rdb_file_parser()
        
        except Exception as e:
            print ("File is empty",e)

        return 

    def stringparser(self, s: str) -> str:
        pass

    def intparser(self, s: str) -> str:
        pass

    def parsekeys(self, regex: str) -> str:
        pass
    
    def valid_file(self, data):
        
        header = data[:5].decode('ascii') 
        version = data[5:10].decode('ascii')

        print(header, version)

        if header != "REDIS":
            raise InvalidRdbFileException(header)
        
        return version
    
    def split_subsections(self, data: str) -> list:

        for position, byte in enumerate(data):
            
            self.position_in_file = position
            byte_hex_val = byte.hex()
            
            if  byte_hex_val in self.subsection_types_set:
                self.subssection_dict_setter(byte_hex_val)


    def subssection_dict_setter(self, subsection_header: str):
        try:
            generic_subsection_handler_method = getattr(self, subsection_header)

            generic_subsection_handler_method(self.position_in_file)
            

        except AttributeError:
            raise DynamicMethodNotFoundException(self, subsection_header)


        
        return data_list






