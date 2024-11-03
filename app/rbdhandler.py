import re
from typing import List
import argparse
from errorhandler.exceptions import InvalidRdbFileException, DynamicMethodNotFoundException

class RdbHandler:

    subsection_types_set: set = set(["FA","FB","FC","FD","FE","FF"])
    subsections_values_dict: dict = {subsection for subsection in subsection_types_set}
    
    file_byte_data: bytes
    position_in_file: int = 0

    

    def read_bits(self, number_of_bits: bytearray, option_for_sub_byte_parsing: bool = False):
        """Reads bits from a byte, from most significant to least significant."""

    
        byte = self.file_byte_data[self.position_in_file]

        if option_for_sub_byte_parsing:
            for i in range(2, number_of_bits):
                yield (byte << (i)) & 1
        else:
            for i in range(number_of_bits):
                yield (byte << (i)) & 1


    def setrbd(self, parse_obj: argparse) -> None:
        
        args= parse_obj.parse_args()

        self.dir = args.dir
        self.file = args.dbfilename

        pass

    def rdb_file_parser(self, file_data) -> List[str]:
        
        version = self.valid_file()
        
        print("RDB version  number ", version)

        self.split_subsections()

    
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
    
    def valid_file(self):
        
        header = self.file_byte_data[:5].decode('ascii') 
        version = self.file_byte_data[5:10].decode('ascii')

        self.position_in_file += 10

        print(header, version)

        if header != "REDIS":
            raise InvalidRdbFileException(header)
        
        return version
    
    def split_subsections(self) -> list:

        byte_hex_val_as_string = "temp"
        
        while byte_hex_val_as_string != "FF":
            
            byte = self.file_byte_data[self.position_in_file]
            
            byte_hex_val_as_string = byte.hex()
            
            if byte_hex_val_as_string in self.subsection_types_set:

                try:
                    generic_subsection_handler_method = getattr(self, byte_hex_val_as_string)

                    generic_subsection_handler_method()

                except AttributeError:
                    raise DynamicMethodNotFoundException(self, byte_hex_val_as_string)

        return

    def length_encoding_decode(self):
        
        first_two_bits_as_string = str(self.read_bits(number_of_bits = 2))

        print(first_two_bits_as_string)

        match first_two_bits_as_string:

            case "00":
                length_of_data_in_bytes = int(str(self.read_bits(number_of_bits = 6, option_for_sub_byte_parsing = True)))
                print(length_of_data_in_bytes)
            
            case "01":
                length_of_data_in_bytes = int(str(self.read_bits(number_of_bits= 6, option_for_sub_byte_parsing = True)))
                self.position_in_file+= 1
                length_of_data_in_bytes = int(str(self.read_bits(number_of_bits= 8)))

            case "10":
                self.position_in_file+= 1
                for i in range(4):
                     string_of_bits_for_length_encoding = str(self.read_bits(number_of_bits= 8))
                length_of_data_in_bytes =int(string_of_bits_for_length_encoding)
            
            case "11":
                format_of_encoded_string = int(str(self.read_bits(number_of_bits = 6, option_for_sub_byte_parsing = True)))
                
                match format_of_encoded_string:
                    
                    case 0:
                        self.position_in_file += 1
                        length_of_integer_in_bits = 8
                    
                    case 1:
                        self.position_in_file += 1
                        length_of_integer_in_bits = 8
                    
                    case 2:
                        self.position_in_file += 1
                        length_of_integer_in_bits = 8

                    case 3:
                        self.position_in_file += 1
                        #clen follows might have to call this method again a little too complex to tackle for now will come back to this
                        

                    



        first_two_bits_as_int = int(first_two_bits_as_string, 2)


       

    
    def fa(self):
        self.position_in_file+=1
        self.length_encoding_decode()










