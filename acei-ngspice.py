#!/usr/bin/env python3

import sys
import subprocess

#Output file name
ACEI_OUT = 'ACEI_OUT.dat'
AC_Measures = 'AC_Measures.txt'
OP_Measures = 'OP_Measures.txt'

def runSimulator(netlist):
	#runs ngspice and gives a timeout of 15 seconds
	try:
		subprocess.run(["ngspice","-b", netlist, "-o", AC_Measures, "-r", OP_Measures], timeout=15)
	except subprocess.TimeoutExpired:
		sys.exit("Simulation ran too long!")

def parseACMeasures():
	measures = {}
	try:
		with open(AC_Measures, 'r') as file:
			for line in file:
				content = line.split()
				if len(content) == 3 and content[1] == '=':
					measures[content[0]] = content[2]
	except:
		print("File with AC measures not found!")

	return measures

def parseOPMeasures():
	measures = {}
	listOfMeas = []
	index = 0
	valuesFound = False
	try:
		with open(OP_Measures, 'r') as file:
			for line in file:
				if '@' in line:
					listOfMeas.append(line.split('\t')[2].split('@')[1].split(')')[0].replace('[', '_').replace(']', ''))
				elif valuesFound and index <= numberVariables:
					if index == 0:
						measures[listOfMeas[index]] = line.split()[1]
					else:
						measures[listOfMeas[index]] = line.split()[0]
					index += 1
				elif 'Values:' in line:
					valuesFound = True
					numberVariables = len(listOfMeas) - 1
	except IOError:
		print("File with OP measures not found!")
	return measures

def writeKeys(measures, outFile):
	for key in measures.keys():
		outFile.write(key + '\t')

def writeValues(measures, outFile):
	for value in measures.values():
		outFile.write(value + '\t')

def getOutputFile(measuresAC, measuresOP):
	try:
		with open(ACEI_OUT, 'w') as outFile:
			writeKeys(measuresAC, outFile)
			writeKeys(measuresOP, outFile)
			outFile.write('\n')
			writeValues(measuresAC, outFile)
			writeValues(measuresOP, outFile)
	except IOError:
		print("Error opening output file!")

def removePreviousFiles():
	#Remove old output files if exist (NGSpice and parser outputs)
	if len(sys.argv) == 3:
		subprocess.call(['rm','-f', sys.argv[2]])
	else:
		subprocess.call(['rm','-f',ACEI_OUT])
	subprocess.call(['rm','-f',AC_Measures])
	subprocess.call(['rm','-f',OP_Measures])
		
def main():

	removePreviousFiles()

	runSimulator(sys.argv[1])
	measuresAC = parseACMeasures()
	#print(measuresAC)

	measuresOP = parseOPMeasures()
	#print(measuresOP)

	getOutputFile(measuresAC, measuresOP)

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		pass
	else:
		main()

	