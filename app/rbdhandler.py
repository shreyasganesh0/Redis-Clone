import re
from typing import List
import argparse
from .errorhandler.exceptions import InvalidRdbFileException, DynamicMethodNotFoundException

class RdbHandler:

    subsection_types_set: set = set([250,251,252,253,254,255])
    subsections_values_dict: dict = {subsection:{} for subsection in [250,251,252,253,254,255]}
    
    file_byte_data: bytes
    position_in_file: int = 0

    

    def read_bits(self, number_of_bits: bytearray, option_for_sub_byte_parsing: bool = False):
        """Reads bits from a byte, from most significant to least significant."""

    
        byte_val = self.file_byte_data[self.position_in_file]

        print(byte_val,"byte", type(byte_val))

        bits_list =[]

        if option_for_sub_byte_parsing:
            for i in range(6,-1,-1):
                print("here bitspar")
                bits_list.append( str((byte_val >> (i)) & 1))
        else:
            for i in range(8,6,-1):
                bits_list.append( str((byte_val >> (i)) & 1))

        return "".join(bits_list)


    def setrbd(self, parse_obj: argparse) -> None:
        
        args= parse_obj.parse_args()

        self.dir = args.dir
        self.file = args.dbfilename

        pass

    def rdb_file_parser(self) -> List[str]:
        
        version = self.valid_file()
        
        print("RDB version number ", version)

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
        
        header = str(self.file_byte_data[:5],'utf-8')
        version = str(self.file_byte_data[5:9],'utf-8')

        self.position_in_file = 9

        print(header, version)

        if header != "REDIS":
            raise InvalidRdbFileException(header)
        
        return version
    
    def split_subsections(self) -> list:

        while self.position_in_file <len(self.file_byte_data):
        
            byte_val =self.file_byte_data[self.position_in_file]

            print(byte_val)

            if byte_val in self.subsection_types_set:
                current_header_for_data = byte_val

                self.position_in_file+=1
                
            
            else:
                print("curr byte header", current_header_for_data)
                
                if current_header_for_data == 251:
                    print("In 251")
                    size_no_expiry_hash_table = self.file_byte_data[self.position_in_file]
                    self.subsections_values_dict[current_header_for_data]["no_expiry_dict_size"]=size_no_expiry_hash_table
                    self.position_in_file +=1

                    size_expiry_hash_table = self.file_byte_data[self.position_in_file]
                    self.subsections_values_dict[current_header_for_data]["expiry_dict_size"]=size_expiry_hash_table

                    self.position_in_file +=1

                    continue

                elif current_header_for_data ==250:

                    
                    print("In 250")
                    length_of_bytes = self.length_encoding_decode()
                    key = str(self.file_byte_data[self.position_in_file:self.position_in_file+length_of_bytes+1],'utf-8')
                    print(key)

                    self.subsections_values_dict[current_header_for_data][key]=""

                    print("key", key)

                    self.position_in_file+=length_of_bytes+1
                    
                    length_of_bytes= self.length_encoding_decode()

                    data = str(self.file_byte_data[self.position_in_file:self.position_in_file+length_of_bytes+1],'utf-8')
                    self.subsections_values_dict[current_header_for_data][key]=data
                    
                    self.position_in_file+=length_of_bytes+1
                    continue

                elif current_header_for_data == 255:

                    print("In 255e")
                    db_number_int = self.file_byte_data[self.position_in_file]
                    self.subsections_values_dict[current_header_for_data] += db_number_int
                    self.position_in_file+=1
                    continue
                
                elif current_header_for_data == 254 and "time_expiry_seconds" not in self.subsections_values_dict[current_header_for_data]:
                    print("In 254 ")
                    time_expiry_seconds ="" 
                    for i in range(4):
                        time_expiry_seconds += str(self.file_byte_data[self.position_in_file])
                        self.position_in_file+=1

                    print("time", time_expiry_seconds)
                    self.subsections_values_dict[current_header_for_data]["time_expiry_seconds"] = int(time_expiry_seconds)
                    self.position_in_file+=1
                    
                    value_type = self.file_byte_data[self.position_in_file]
                    self.subsections_values_dict[current_header_for_data]["value_type"]=value_type 

                    continue
                
                elif current_header_for_data == 253 and "time_expiry_msecs" not in self.subsections_values_dict[current_header_for_data]:
                    print("In 253")
                    time_expiry_seconds = ""
                    for i in range(8):
                        time_expiry_seconds += str(self.file_byte_data[self.position_in_file])
                        self.position_in_file+=1

                    
                    print("time", time_expiry_seconds)
                    self.subsections_values_dict[current_header_for_data]["expiry_time_msec"] = int(time_expiry_seconds)
                    self.position_in_file+=1
                    value_type = self.file_byte_data[self.position_in_file]


                    self.subsections_values_dict[current_header_for_data]["value_type"]=value_type
                    self.position_in_file+=1
                    continue

                elif (current_header_for_data == 253 or current_header_for_data == 254 ) and self.subsections_values_dict[current_header_for_data]["value"] == 255:

                    print("here for now")
                    length_of_bytes = self.length_encoding_decode()
                    key = str(self.file_byte_data[self.position_in_file:self.position_in_file+length_of_bytes+1],'utf-8')


                    self.subsections_values_dict[current_header_for_data][key]=""

                    print("data ", data)

                    self.position_in_file+=length_of_bytes+1
                    
                    length_of_bytes= self.length_encoding_decode()

                    data = str(self.file_byte_data[self.position_in_file:self.position_in_file+length_of_bytes+1],'utf-8')
                    self.subsections_values_dict[current_header_for_data][key]=data

                    self.position_in_file+=length_of_bytes+1

            print(self.subsections_values_dict)
        return

    def length_encoding_decode(self):
        
        first_two_bits_as_string = self.read_bits(number_of_bits = 2)

        print(first_two_bits_as_string, "first two bit")

        match first_two_bits_as_string:

            case "00":
                print("in 00")
                length_of_data_in_bytes = int(self.read_bits(number_of_bits = 6, option_for_sub_byte_parsing = True),2)
                print(length_of_data_in_bytes,"length")
            
            case "01":
                length_of_data_in_bytes = int(self.read_bits(number_of_bits= 6, option_for_sub_byte_parsing = True))
                self.position_in_file+= 1
                length_of_data_in_bytes = int(str(self.read_bits(number_of_bits= 8)))

            case "10":
                print("in 10")
                self.position_in_file+= 1
                string_of_bits_for_length_encoding=""
                for i in range(4):
                     string_of_bits_for_length_encoding += str(self.read_bits(number_of_bits= 8))
                length_of_data_in_bytes =int(string_of_bits_for_length_encoding)
            
            case "11":
                format_of_encoded_string = int(str(self.read_bits(number_of_bits = 6, option_for_sub_byte_parsing = True)))
                
                match format_of_encoded_string:
                    
                    case 0:
                        self.position_in_file += 1
                        length_of_integer_in_bits = 8
                    
                    case 1:
                        self.position_in_file += 1
                        length_of_integer_in_bits = 16
                    
                    case 2:
                        self.position_in_file += 1
                        length_of_integer_in_bits = 32

                    case 3:
                        self.position_in_file += 1
                        #clen follows might have to call this method again a little too complex to tackle for now will come back to this
                length_of_data_in_bytes =length_of_integer_in_bits //8

        return length_of_data_in_bytes
        first_two_bits_as_int = int(first_two_bits_as_string, 2)

    











