#!/usr/bin/env python3

import sys
import subprocess
import glob
import threading
import os
import shutil
import time

#Output file name
ACEI_OUT = 'ACEI_OUT.dat'
AC_Measures = 'AC_Measures'
OP_Measures = 'OP_Measures'
Extension = '.txt'

#Corners file
Corners = 'corners.inc'

def runSimulation(netlist, corner):
	currDirectory = os.getcwd()
	#runs ngspice and gives a timeout of 15 seconds
	try:
		outputAC = AC_Measures + corner + Extension
		outputOP = OP_Measures + corner + Extension
		subprocess.run(["ngspice", "-b", netlist, "-o", outputAC, "-r", outputOP], timeout=15)
	except subprocess.TimeoutExpired:
		sys.exit("Simulation ran too long!")

def parseACMeasures(corner):
	measures = {}
	filename = AC_Measures + corner + Extension

	try:
		with open(filename, 'r') as file:
			for line in file:
				content = line.split()
				if len(content) == 3 and content[1] == '=':
					measures[content[0]] = content[2]
	except:
		print("File with AC measures not found!")

	return measures

def parseOPMeasures(corner):
	measures = {}
	listOfMeas = []
	index = 0
	valuesFound = False
	filename = OP_Measures + corner + Extension
	
	try:
		with open(filename, 'r') as file:
			for line in file:
				if '@' in line:
					listOfMeas.append(line.split('\t')[2].split('@')[1].split(')')[0].replace('[', '_').replace(']', '').replace('.', '_'))
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
	if len(sys.argv) == 3:
		filename = sys.argv[2]
	else:
		filename = ACEI_OUT

	try:
		with open(filename, 'w') as outFile:
			for i in range(len(measuresAC)):
				outFile.write('Cornr#\t')
				writeKeys(measuresAC[i], outFile)
				writeKeys(measuresOP[i], outFile)
			outFile.write('\n')
			outFile.write('0 ')
			for i in range(len(measuresAC)):
				writeValues(measuresAC[i], outFile)
				writeValues(measuresOP[i], outFile)
	except IOError:
		print("Error opening output file!")

def removePreviousFiles():
	#Remove old output files if exist (NGSpice and parser outputs)
	if len(sys.argv) == 3:
		subprocess.call(['rm','-f', sys.argv[2]])
	else:
		subprocess.call(['rm','-f', ACEI_OUT])
	removeOutputFiles()
	removeNetlists()

def removeOutputFiles():
	for f in glob.glob('*_Measures*'):
		os.remove(f)

def removeNetlists():
	for f in glob.glob(sys.argv[1].split('.')[0] + '_*'):
		os.remove(f)

def buildNetlistsWithCorners(netlists, corners):
	currDirectory = os.getcwd()
	try:
		with open(Corners, 'r') as file:
			for line in file:
				if '.lib' in line:
					corner = line.split()[2]
					corners.append(corner)
					netlistName = copyNetlist(currDirectory, corner)
					netlists.append(netlistName)
					changeLibrary(netlistName, line, corner)
	except IOError:
		print("Cannot find corners file!")

	return netlists, corners

def copyNetlist(folder, corner):
	netlist, ext = sys.argv[1].split('.')
	netlistName = os.path.join(folder, netlist + '_' + corner + '.' + ext)
	shutil.copy(os.path.join(folder, sys.argv[1]), netlistName)
	return netlistName

def changeLibrary(netlist, library, corner):
	lib = glob.glob('*.lib')[0]
	try:
		with open(netlist, 'r') as file:
			content = file.read().replace('.INC "' + lib + '"', library)
		with open(netlist, 'w') as file: 
			file.write(content)
	except IOError:
		print('Error changing library!')
		
def simulation(corner, netlist, index, measuresAC, measuresOP):
	runSimulation(netlist, corner)
	measuresAC[index] = parseACMeasures(corner)
	measuresOP[index] = parseOPMeasures(corner)

def main():

	start = time.time()
	netlists = []
	corners = []
	threads = []
	removePreviousFiles()
	
	netlists.append(sys.argv[1])
	corners.append('TT')

	netlists, corners = buildNetlistsWithCorners(netlists, corners)

	#Dictionaries that will hold AC and OP measures of all corners
	measuresAC = [{} for n in netlists]
	measuresOP = [{} for n in netlists]

	#Parallel
	for i in range(len(netlists)):
		t = threading.Thread(target=simulation, args=(corners[i], netlists[i], i, measuresAC, measuresOP))
		threads.append(t)
		t.start()

	#Wait for threads to finish processing files
	for t in threads:
		t.join()

	#Not Parallel
	"""for i in range(len(netlists)):
		simulation(corners[i], netlists[i], i, measuresAC, measuresOP)"""

	getOutputFile(measuresAC, measuresOP)
	removeOutputFiles()
	removeNetlists()

	print('Time: ', time.time() - start)

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		sys.exit("No netlist was given!")
	else:
		main()

	