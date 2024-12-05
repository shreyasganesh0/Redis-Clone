
from datetime import datetime, timedelta, timezone
from .commandhandler import CommandExecutor
import struct
import re
from typing import List
import argparse
from .errorhandler.exceptions import InvalidRdbFileException, DynamicMethodNotFoundException

class RdbHandler:

    subsection_types_set: set = set([250,251,252,253,254,255])
    subsections_values_dict: dict = {subsection:{} for subsection in [250,251,252,253,254,255,"misc_kvs"]}
    
    file_byte_data: bytes
    position_in_file: int = 0

    

    def read_bits(self, number_of_bits: bytearray, option_for_sub_byte_parsing: bool = False):
        """Reads bits from a byte, from most significant to least significant."""

    
        byte_val = self.file_byte_data[self.position_in_file]

        bits_list =[]
        print("byte calc", byte_val)

        if option_for_sub_byte_parsing:
            for i in range(6,-1,-1):
                bits_list.append( str((byte_val >> (i)) & 1))
        else:
            for i in range(8,6,-1):
                bits_list.append( str((byte_val >>(i)) & 1))

        return "".join(bits_list)


    def setrbd(self, parse_obj: argparse) -> None:
        
        args= parse_obj.parse_args()

        self.dir = args.dir
        self.file = args.dbfilename

        pass

    def rdb_file_parser(self) :
        
        version = self.valid_file()
        
        print("RDB version number ", version)

        self.split_subsections()
        return
    
    def filehandler(self, obj ) -> None:

        
        fpath = f'{obj.dir}/{obj.file}'

        try:
            with open(fpath, 'rb') as f:
               
                self.file_byte_data = f.read()
                print(self.file_byte_data)
                self.rdb_file_parser()
                self.set_rdb_keys(obj)

        except Exception as e:
            print ("File is empty",e)

        return
    def replica_filehandler(self, obj, data):
        try:
            self.file_byte_data = data
            self.rdb_file_parser()
            self.set_rdb_keys(obj)
        except Exception as e:
            print(e)


    def valid_file(self):
        
        header = str(self.file_byte_data[:5],'utf-8')
        version = str(self.file_byte_data[5:9],'utf-8')

        self.position_in_file = 9

        print(header, version)

        if header != "REDIS":
            raise InvalidRdbFileException(header)
        
        return version
    
    def split_subsections(self) -> list:
        skip_to_no_expiry = False

        while self.position_in_file <len(self.file_byte_data):
        
            byte_val =self.file_byte_data[self.position_in_file]

            print(byte_val,'byte val curr')

            if byte_val in self.subsection_types_set: 
                current_header_for_data = byte_val

                self.position_in_file+=1
                   
            
            else:
                if skip_to_no_expiry:
                    current_header_for_data = "misc_kvs"
                print("curr byte header", current_header_for_data)
                 
                
                if current_header_for_data == 251:
                    print("In 251")
                    size_no_expiry_hash_table = self.file_byte_data[self.position_in_file]
                    self.subsections_values_dict[current_header_for_data]["no_expiry_dict_size"]=size_no_expiry_hash_table
                    self.position_in_file +=1

                    size_expiry_hash_table = self.file_byte_data[self.position_in_file]
                    self.subsections_values_dict[current_header_for_data]["expiry_dict_size"]=size_expiry_hash_table

                    self.position_in_file +=1
                    print(self.subsections_values_dict[current_header_for_data]["expiry_dict_size"]," exp")
                    print(self.subsections_values_dict[current_header_for_data]["no_expiry_dict_size"],"no exp")
                    if self.subsections_values_dict[current_header_for_data]['expiry_dict_size']==0 and self.subsections_values_dict[current_header_for_data]["no_expiry_dict_size"] >0:
                        skip_to_no_expiry =True                                                                                
                    

                elif current_header_for_data == 252 or current_header_for_data == 253 or current_header_for_data == "misc_kvs":
                    if  self.subsections_values_dict[251]["expiry_dict_size"] > 0:
                        self.subsections_values_dict[251]["expiry_dict_size"]-=1
                        
                        print("in the expiry")
                        print(current_header_for_data,"curr head")
                        
                        if current_header_for_data == 252:
                            print("In 252 ",self.file_byte_data[self.position_in_file:self.position_in_file+8])
                            
                            time_expiry_seconds = int.from_bytes(self.file_byte_data[self.position_in_file:self.position_in_file+9],byteorder='little',signed= False) 
                            self.position_in_file+=8
                            print(self.file_byte_data[self.position_in_file])
                            #time_expiry_seconds = int.from_bytes(time_expiry_seconds, byteorder='little', signed=False)

                            print("time", time_expiry_seconds)
                            
                            value_type = self.file_byte_data[self.position_in_file]


                            self.position_in_file+=1
        
                            print("here for now")
                            length_of_bytes = self.length_encoding_decode()
                            key = str(self.file_byte_data[self.position_in_file+1:self.position_in_file+length_of_bytes+1],'utf-8')


                            self.subsections_values_dict[current_header_for_data][(key,time_expiry_seconds,value_type)]=""

                            print("key", key)

                            self.position_in_file+=length_of_bytes+1
                            
                            length_of_bytes= self.length_encoding_decode()

                            data = str(self.file_byte_data[self.position_in_file+1:self.position_in_file+length_of_bytes+1],'utf-8')
                            self.subsections_values_dict[current_header_for_data][(key,time_expiry_seconds,value_type)]=data
                            print("data", data)
                            self.position_in_file+=length_of_bytes+1
                        
                        elif current_header_for_data == 253:
                            print("In 253")
                            time_expiry_seconds = self.file_byte_data[self.position_in_file:self.position_in_file+5]
                            self.position_in_file +=4

                            
                            time_expiry_seconds = int.from_bytes(time_expiry_seconds, byteorder='little', signed=False)
                            print("time", time_expiry_seconds)

                            value_type = self.file_byte_data[self.position_in_file]

                            self.position_in_file+=1
                            

                            print("here for now")
                            length_of_bytes = self.length_encoding_decode()
                            key = str(self.file_byte_data[self.position_in_file+1:self.position_in_file+length_of_bytes+1],'utf-8')


                            self.subsections_values_dict[current_header_for_data][(key, time_expiry_seconds,value_type)]=""

                            print("key ", key)

                            self.position_in_file+=length_of_bytes+1
                            
                            length_of_bytes= self.length_encoding_decode()

                            data = str(self.file_byte_data[self.position_in_file+1:self.position_in_file+length_of_bytes+1],'utf-8')
                            self.subsections_values_dict[current_header_for_data][(key,time_expiry_seconds, value_type)]=data

                            self.position_in_file+=length_of_bytes+1

                    else:
                        print("in the no expiry")
                        count = self.subsections_values_dict[251]["no_expiry_dict_size"] 
                        current_header_for_data="misc_kvs" 
                        value_type = self.file_byte_data[self.position_in_file]
                        self.subsections_values_dict[current_header_for_data]["value_type"]=value_type
                        self.position_in_file+=1
                        while count >0:
                            
                            length_of_bytes = self.length_encoding_decode()
                            key = str(self.file_byte_data[self.position_in_file+1:self.position_in_file+length_of_bytes+1],'utf-8')


                            self.subsections_values_dict[current_header_for_data][key]=""

                            print("key",key)

                            self.position_in_file+=length_of_bytes+1
                            
                            length_of_bytes= self.length_encoding_decode()

                            data = str(self.file_byte_data[self.position_in_file+1:self.position_in_file+length_of_bytes+1],'utf-8')
                            self.subsections_values_dict[current_header_for_data][key]=data

                            print("data ", data)
                            self.position_in_file+=length_of_bytes+2
                            count-=1
                        skip_to_no_expiry =False
                        self.position_in_file-=1
                        print(self.file_byte_data[self.position_in_file-1],"exit val")

                elif current_header_for_data ==250:

                    print("In 250")
                    length_of_bytes = self.length_encoding_decode()
                    key = str(self.file_byte_data[self.position_in_file+1:self.position_in_file+length_of_bytes+1],'utf-8')
                    key=key[:]

                    self.subsections_values_dict[current_header_for_data][key]=""

                    print("key", key)

                    self.position_in_file+=length_of_bytes+1
                    
                    length_of_bytes= self.length_encoding_decode()

                    data = (self.file_byte_data[self.position_in_file+1:self.position_in_file+length_of_bytes+1])

                    print("data", data)

                    self.subsections_values_dict[current_header_for_data][key]=data
                    
                    self.position_in_file+=length_of_bytes+1

                elif current_header_for_data == 254:

                    print("In 254")
                    db_number_int = self.file_byte_data[self.position_in_file]
                    self.subsections_values_dict[current_header_for_data]["db_number"]= db_number_int
                    self.position_in_file+=1
                    continue
                elif current_header_for_data == 255:
                    print("in 255")
                    crc_checksum=""
                    for i in range(8):
                        crc_checksum += str(self.file_byte_data[self.position_in_file])
                        self.position_in_file+=1
                    self.subsections_values_dict[current_header_for_data]["crcchecksum"]=crc_checksum
                    self.position_in_file+=2
                    continue
            print(self.subsections_values_dict)
        return 

    def length_encoding_decode(self):
        
        first_two_bits_as_string = self.read_bits(number_of_bits = 2)

        print(first_two_bits_as_string, "first two bit")

        match first_two_bits_as_string:

            case "00":
                length_of_data_in_bytes = int(self.read_bits(number_of_bits = 6, option_for_sub_byte_parsing = True),2)
            
            case "01":
                length_of_data_in_bytes = int(self.read_bits(number_of_bits= 6, option_for_sub_byte_parsing = True),2)
                self.position_in_file+= 1
                length_of_data_in_bytes = 0

            case "10":
                print("in 10")
                self.position_in_file+= 1
                string_of_bits_for_length_encoding=""
                for i in range(4):
                     string_of_bits_for_length_encoding += str(self.read_bits(number_of_bits= 8))
                length_of_data_in_bytes = int(string_of_bits_for_length_encoding)
            
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
        print(length_of_data_in_bytes, " length in bytes")
        return length_of_data_in_bytes
    

    def set_rdb_keys(self, redis_obj):
        

        print("here in keys",self.subsections_values_dict)

        total_key_val = {i:self.subsections_values_dict[i] for i in self.subsections_values_dict if i in set([253,252,"misc_kvs"])}

        print(total_key_val)

        command = CommandExecutor()
        resp=[]
        for key in total_key_val:
            if key == 252:
                for kvs in total_key_val[key]:

                    command.set(redis_obj, (0,kvs[0], total_key_val[key][kvs],0,(kvs[1])-int(datetime.now(timezone.utc).timestamp()*1000)))
            elif key == 253:
                for kvs in total_key_val[key]:

                    command.set(redis_obj, (0,kvs[0], total_key_val[key][kvs],0,kvs[1]-int(datetime.now(timezone.utc).timestamp())))

            
            else:
                for kvs in total_key_val[key]:

                    if kvs == "value_type":
                        continue
                    else:
                        command.set(redis_obj, (0,kvs, total_key_val[key][kvs]))