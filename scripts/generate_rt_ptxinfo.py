# Copyright (c) 2022, Mohammadreza Saed, Yuan Hsi Chou, Lufei Liu, Tor M. Aamodt,
# The University of British Columbia
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution. Neither the name of
# The University of British Columbia nor the names of its contributors may be
# used to endorse or promote products derived from this software without
# specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


# Usage
# python3 generate_rt_<filename>.ptx
# It will generate <filename>.ptxinfo in the same location as the ptx file

import os
import sys
import subprocess
import random

inputfile = sys.argv[1]

proc = subprocess.Popen(["ptxas " + inputfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
stdout, stderr = proc.communicate()
#print("program output:")


unknown_symbols = []
unknown_op_name = []
unknown_op_line = []

lines = str(stderr, 'utf-8').splitlines()
for l in lines:
    #print(l)
    if (l.find("Unknown symbol") != -1):
        idx1 = l.index("'")
        idx2 = l.index("'", idx1+1)
        #print(idx1, idx2)
        #print(l[idx1+1:idx2])
        unknown_symbols.append(l[idx1+1:idx2])
    
    if (l.find("Not a name of any known instruction") != -1):
        idx1 = l.index("'")
        idx2 = l.index("'", idx1+1)
        #print(idx1, idx2)
        #print(l[idx1+1:idx2])
        unknown_op_name.append(l[idx1+1:idx2])

        idx3 = l.index("line ")
        idx4 = l.index(";")
        #print(l[idx3+5:idx4])
        unknown_op_line.append(int(l[idx3+5:idx4]))

unknown_symbols = list(set(unknown_symbols)) # removes duplicates

print("Parsed unknown symbols and ops.")
# print(unknown_symbols)
print(unknown_op_name)
#print(unknown_op_line)



f = open(inputfile, 'r')
tempoutput = open("temp_ptxas_shader.ptx", 'w')

# Create the symbol table
symbol_table = {}
is_vec = {}

for l in f.readlines():
    if (l.find(".reg") != -1):
        chunks = l.replace(";", "").split()
        if (len(chunks) == 3):
            symbol_table[chunks[-1]] = chunks[-2]
            is_vec[chunks[-1]] = False
        elif (len(chunks) == 4):
            symbol_table[chunks[-1]] = chunks[-2]
            is_vec[chunks[-1]] = True

print("Created symbol table")
print(symbol_table)
#print(is_vec)
initial_symbol_number = len(symbol_table)
print("initial symbol number: ",initial_symbol_number)


# Writing a fake ptx file for ptxas
linenum = 0

f.seek(0)
for l in f.readlines():
    linenum += 1

    if (linenum in unknown_op_line):
        idx = unknown_op_line.index(linenum)
        #print("this is the line")
        #print("// " + l)
        segs = l.split("//")[0].replace(",", "").replace(";", "").split()
        #print(segs)
        if(segs[0] == unknown_op_name[idx]):
            #print("unknown op matches")
            segs.remove(segs[0])
            operands = []
            for item in segs:
                #print(item)
                if(not item.isnumeric()):
                    operands.append(item)
            #print(operands)
            num_operands = len(operands)
            #print(num_operands)

            for i in reversed(range(num_operands-1)):
                #print(operands[i+1] + " is type " + symbol_table[operands[i+1]])
                #print(operands[i] + " is type " + symbol_table[operands[i]])

                # Convert unknown op to convert chain
                # Printing Instruction
                if((symbol_table[operands[i]][2:] != symbol_table[operands[i+1]][2:])): # When bit sizes dont match
                    #print(symbol_table[operands[i]][2:])
                    #print(symbol_table[operands[i+1]][2:])
                    #print(".reg " + symbol_table[operands[i+1]][1] + symbol_table[operands[i]][2:] + " " + operands[i+1] + "_tempreg;") # make temp reg
                    tempoutput.write(".reg " + symbol_table[operands[i+1]][0:2] + symbol_table[operands[i]][2:] + " " + operands[i+1] + "_tempreg" + str(linenum) +";\n")
                    #print("cvt." + symbol_table[operands[i+1]][1] + symbol_table[operands[i]][2:]+ symbol_table[operands[i+1]] + " " + operands[i+1] + "_tempreg, " + operands[i+1] + ";")
                    tempoutput.write("cvt." + symbol_table[operands[i+1]][1] + symbol_table[operands[i]][2:]+ symbol_table[operands[i+1]] + " " + operands[i+1] + "_tempreg" + str(linenum) + ", " + operands[i+1] + ";\n")

                    if(symbol_table[operands[i]] == ".b32"):
                        #print("mov.b32 ", end='')
                        tempoutput.write("mov.b32 ")
                    elif(symbol_table[operands[i]] == ".b64"):
                        #print("mov.b64 ", end='')
                        tempoutput.write("mov.b64 ")
                    elif(".b" in symbol_table[operands[i+1]]):
                        #print("mov" + symbol_table[operands[i]] + " ", end='')
                        tempoutput.write("mov" + symbol_table[operands[i]] + " ")
                    else:
                        #print("cvt", end='')
                        tempoutput.write("cvt")

                        if((".f" in symbol_table[operands[i]] and ".f" not in symbol_table[operands[i+1]]) or (".f" not in symbol_table[operands[i]] and ".f" in symbol_table[operands[i+1]])):
                            if(".f" in symbol_table[operands[i]]):
                                #print(".rn", end='')
                                tempoutput.write(".rn")
                            else:
                                #print(".rni", end='')
                                tempoutput.write(".rni")
                    
                    # Operand printing
                    if(".b" not in symbol_table[operands[i]] and ".b" not in symbol_table[operands[i+1]]):
                        #print(symbol_table[operands[i]] + symbol_table[operands[i+1]] + " ", end='')
                        tempoutput.write(symbol_table[operands[i]] + symbol_table[operands[i+1]][0:2] + symbol_table[operands[i]][2:] + " ")

                    #print(operands[i], end='')
                    tempoutput.write(operands[i])

                    if(is_vec[operands[i]]):
                        #print(".x", end='')
                        tempoutput.write(".x")
                    
                    #print(", " + operands[i+1] + "_tempreg", end='')
                    tempoutput.write(", " + operands[i+1] + "_tempreg" + str(linenum))

                    if(is_vec[operands[i+1]]):
                        #print(".x", end='')
                        tempoutput.write(".x")
                    
                    #print(";")
                    tempoutput.write(";\n")
                
                else: # When the bit sizes match but type is different
                    if(symbol_table[operands[i]] == ".b32"):
                        #print("mov.b32 ", end='')
                        tempoutput.write("mov.b32 ")
                    elif(symbol_table[operands[i]] == ".b64"):
                        #print("mov.b64 ", end='')
                        tempoutput.write("mov.b64 ")
                    elif(".b" in symbol_table[operands[i+1]]):
                        #print("mov" + symbol_table[operands[i]] + " ", end='')
                        tempoutput.write("mov" + symbol_table[operands[i]] + " ")
                    else:
                        #print("cvt", end='')
                        tempoutput.write("cvt")

                        if((".f" in symbol_table[operands[i]] and ".f" not in symbol_table[operands[i+1]]) or (".f" not in symbol_table[operands[i]] and ".f" in symbol_table[operands[i+1]])):
                            if(".f" in symbol_table[operands[i]]):
                                #print(".rn", end='')
                                tempoutput.write(".rn")
                            else:
                                #print(".rni", end='')
                                tempoutput.write(".rni")
                    
                    # Operand printing
                    if(".b" not in symbol_table[operands[i]] and ".b" not in symbol_table[operands[i+1]]):
                        #print(symbol_table[operands[i]] + symbol_table[operands[i+1]] + " ", end='')
                        tempoutput.write(symbol_table[operands[i]] + symbol_table[operands[i+1]] + " ")

                    #print(operands[i], end='')
                    tempoutput.write(operands[i])

                    if(is_vec[operands[i]]):
                        #print(".x", end='')
                        tempoutput.write(".x")
                    
                    #print(", " + operands[i+1], end='')
                    tempoutput.write(", " + operands[i+1])

                    if(is_vec[operands[i+1]]):
                        #print(".x", end='')
                        tempoutput.write(".x")
                    
                    #print(";")
                    tempoutput.write(";\n")



    else:
        # check op. In NIR, different types can do math directly, while in PTX, we need to convert
        segs = l.split("//")[0].replace(",", "").replace(";", "").split()
        # print(segs)
        if segs:
            if(segs[0].split('.')[0] == "min"):
                # get three operand and check their types
                dest, src1, src2 = segs[1], segs[2], segs[3]
                newsrcs = [None, None]
                for i, src in enumerate([src1, src2]):
                    # check type
                    if symbol_table[src] != symbol_table[dest]:
                        # different type, need to convert
                        # new reg declaration
                        new_convert_temp_reg_name = src + "_cvtr_frm_" + str(linenum)
                        # check that the new reg is not already declared
                        while new_convert_temp_reg_name in symbol_table:
                            new_convert_temp_reg_name = new_convert_temp_reg_name + "_rnd_" + str(random.randint(0, 1000000))
                        symbol_table[new_convert_temp_reg_name] = symbol_table[dest]
                        is_vec[new_convert_temp_reg_name] = is_vec[dest]
                        # add convertion line
                        conversion_line = ".reg " + symbol_table[dest] + " " + new_convert_temp_reg_name + ";\n"
                        tempoutput.write(conversion_line)
                        if symbol_table[dest] == ".s32" and symbol_table[src] == ".f32":
                            cmd = "cvt.rni"
                        else:
                            print("not implemented conversion of " + symbol_table[src] + " to " + symbol_table[dest])
                        tempoutput.write(cmd + symbol_table[dest] + symbol_table[src] + " " + new_convert_temp_reg_name + ", " + src + ";\n")
                        newsrcs[i] = new_convert_temp_reg_name
                for i, src in enumerate(newsrcs):
                    if src is not None:
                        segs[i + 2] = src
                editedline = segs[0] + " " + segs[1] + ', ' + segs[2] + ', ' + segs[3] + ';' + " //" + " ".join(l.split("//")[1:]) if(l.split("//")[1:]) else ""
                tempoutput.write(editedline)
                
                # tempoutput.write(l)
            elif(segs[0].split('.')[0] == "or"):
                dest, src1, src2 = segs[1], segs[2], segs[3]
                newsrcs = [None, None]
                for i, src in enumerate([src1, src2]):
                    # check type
                    if symbol_table[src] != symbol_table[dest]:
                        # different type, need to convert
                        # new reg declaration
                        new_convert_temp_reg_name = src + "_cvtr_frm_" + str(linenum)
                        # check that the new reg is not already declared
                        while new_convert_temp_reg_name in symbol_table:
                            new_convert_temp_reg_name = new_convert_temp_reg_name + "_rnd_" + str(random.randint(0, 1000000))
                        symbol_table[new_convert_temp_reg_name] = symbol_table[dest]
                        is_vec[new_convert_temp_reg_name] = is_vec[dest]
                        # add convertion line
                        conversion_reg_line = ".reg " + symbol_table[dest] + " " + new_convert_temp_reg_name + ";\n"
                        tempoutput.write(conversion_reg_line)
                        if symbol_table[dest] == ".pred" and symbol_table[src] == ".b32":
                            cmd = "setp.ne.b32 " + new_convert_temp_reg_name + ", " + src + ", 0;\n"
                        else:
                            print("not implemented conversion of " + symbol_table[src] + " to " + symbol_table[dest])
                        tempoutput.write(cmd)
                        newsrcs[i] = new_convert_temp_reg_name
                for i, src in enumerate(newsrcs):
                    if src is not None:
                        segs[i + 2] = src
                editedline = segs[0] + " " + segs[1] + ', ' + segs[2] + ', ' + segs[3] + ';' + " //" + " ".join(l.split("//")[1:]) if(l.split("//")[1:]) else ""
                tempoutput.write(editedline)
                
                # tempoutput.write(l)
            else:
                tempoutput.write(l)
        else:
            # print(l)
            tempoutput.write(l)

    if (l.find("/* preds: */") != -1):
        #print(".reg .f64 tempuse;")
        #tempoutput.write(".reg .f64 tempuse;\n")

        # no unknown symbols
        for symbol in unknown_symbols:
            #print(".reg .v4 .f32 " + symbol + ";")
            tempoutput.write(".reg .v4 .f32 " + symbol + ";\n")
            symbol_table[symbol] = ".f32"
            is_vec[symbol] = True



f.close()
tempoutput.close()

# Run PTXAS on the tempoutput and get ptxinfo then delete the tempoutput
fout = open(inputfile+"info", 'w')
proc = subprocess.Popen(["ptxas -v -m 32 " + "temp_ptxas_shader.ptx"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
stdout, stderr = proc.communicate()
lines = str(stderr, 'utf-8').splitlines()
for l in lines:
    print(l)
    fout.writelines(l+"\n")

# os.system("rm -rf temp_ptxas_shader.ptx")
os.system("rm -rf elf.o")