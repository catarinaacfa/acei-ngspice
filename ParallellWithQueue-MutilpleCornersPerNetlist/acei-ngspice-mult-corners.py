#!/usr/bin/env python3

import sys
import subprocess
import glob
import threading
import os
import shutil
import time
import queue

MeasuresOutput = 'Measures'
Extension = '.txt'

#Corners file
Corners = 'corners.inc'
#Design Variables File
VariablesFile = 'design_var.inc'

#Runs each netlist in interactive mode and saves the standard output to a file
def runSimulation(netlist, corner):
	#runs ngspice and gives a timeout of 30 seconds
	try:
		output = MeasuresOutput + corner + Extension
		with open(output, 'w') as f:
			subprocess.run(['ngspice', netlist], stdout=f, timeout=30)
	except subprocess.TimeoutExpired:
		sys.exit("Simulation ran too long!")

#Opens the ouput file of the simulation and writes its content to a dictionary to be further printed in the output file
def parseMeasures(corner):
	measures = {}
	filename = MeasuresOutput + corner + Extension

	try:
		with open(filename, 'r') as file:
			for line in file:
				content = line.split()
				if len(content) == 3 and content[1] == '=':
					measures[content[0]] = content[2]
	except:
		print("Output file not found!")

	return measures

#Goes through a dictionary and print ist keys
def writeKeys(measures, outFile):
	for key in measures.keys():
		outFile.write(key + '\t')

#Goes through a dictionary and print ist values
def writeValues(measures, outFile):
	for value in measures.values():
		outFile.write(value + '\t')

#Writes the output file which will be given to AIDA as input
def getOutputFile(measures):
	if sys.argv[1] == '--corners':
		filename = sys.argv[3]
	else:
		filename = sys.argv[2]

	try:
		with open(filename, 'w') as outFile:
			for i in range(len(measures)):
				outFile.write('Cornr#\t')
				writeKeys(measures[i], outFile)
			outFile.write('\n')
			for i in range(len(measures)):
				outFile.write(str(i) + ' ')
				writeValues(measures[i], outFile)
			outFile.write('\n')
	except IOError:
		print("Error opening output file!")

#Removes the output files and netlists generated
def removePreviousFiles():
	#Remove old output files if exist (NGSpice and parser outputs)
	if len(sys.argv) == 3:
		subprocess.call(['rm','-f', sys.argv[2]])
	else:
		subprocess.call(['rm','-f', ACEI_OUT])
	removeOutputFiles()
	removeNetlists()

#Removes the ouput files
def removeOutputFiles():
	for f in glob.glob('*Measures*'):
		os.remove(f)

#Remove design variables files generated
def removeDesignVarIncFiles():
	for f in glob.glob('design_var_*'):
		os.remove(f)

#Removes netlist files generated (when running corners)
def removeNetlists():
	for f in glob.glob(sys.argv[2].split('.')[0] + '_*'):
		os.remove(f)

#Builds a netlist from corners (is possible to change multiple corners at once, i.e., in the same netlist)
# - library: finds the .lib pattern
# - Temperature: finds the .TEMP card and changes its value
# - Parameters: copies the design_var.inc file, changes the paramaters values and includes that new file in the netlist
def buildNetlistsWithCorners(q):
	cornersDict = dict()
	paramFound = False
	index = 1
	try:
		with open(Corners, 'r') as file:
			for line in file:
				if '.ALTER' in line:
					cornerName = line.split()[1]
					cornersDict[cornerName] = list()
				elif line.strip():
					if '.PARAM' in line:
						paramFound = True
					else:
						if paramFound:
							cornersDict[cornerName].append('.PARAM ' + line)
							paramFound = False
						else:
							cornersDict[cornerName].append(line)

		for corner, values in cornersDict.items():
			netlistName = copyFile(sys.argv[2], corner)
			paramsToChange = list()
			cornersToChange = list()
			for v in values:
				if '.PARAM' in v:
					paramsToChange.append(v)
				else:
					cornersToChange.append(v)

			if paramsToChange:
				newVariablesFileName = copyFile(VariablesFile, corner) #copy design variables file
				#cornersToChange.append(VariablesFile)
				for param in paramsToChange:
					toReplace = param.split()[1]
					pattern = toReplace.split('=')[0]
					changeFile(newVariablesFileName, toReplace+'\n', pattern[1:])
				changeFile(netlistName, '.include \'' + newVariablesFileName + '\'\n', VariablesFile)
				
			if cornersToChange:
				for c in cornersToChange:
					changeFile(netlistName, c, c.split()[0])

			q.put((index, netlistName, corner))
			index += 1

	except IOError:
		print("Cannot find corners file, only the given netlist will be simulated!")

#Copies the original file to a new one
def copyFile(fileName, nameToAdd):
	file, ext = fileName.split('.')
	newFile  = file + '_' + nameToAdd + '.' + ext
	shutil.copy(fileName, newFile)
	return newFile

#Receives a file, finds the pattern to change and replaces it with the new pattern
def changeFile(fileName, toReplace, pattern):
	patternFound = False
	try:
		with open(fileName, 'r') as file:
			for line in file:
				if pattern in line:
					patternFound = True
					break
			if patternFound:
				file.seek(0)
				content = file.read().replace(line, toReplace)
			else:
				print('Error changing netlist - Pattern not found')
		if patternFound:
			with open(fileName, 'w') as file: 
				file.write(content)
	except IOError:
		print('Error changing netlist!')

#Runs NGSpice for a certain netlist
def simulation(simObj, measures):
	runSimulation(simObj[1], simObj[2])
	measures[simObj[0]] = parseMeasures(simObj[2])

#Goes through a queue and runs a simulation for each netlist
def processNetlists(q, measures):
	while not q.empty():
		simObj = q.get()
		simulation(simObj, measures)
		q.task_done()

def main():

	start = time.time()

	#Queue to hold the netlists
	q = queue.Queue(maxsize=0)

	#Get the number of cores available
	numThreads = os.cpu_count()

	#removePreviousFiles()

	#Check if corners will run
	if(sys.argv[1] == '--corners'):
		q.put((0, sys.argv[2], 'TT'))
		buildNetlistsWithCorners(q)
		netlistsNr = q.qsize()
	else:
		q.put((0, sys.argv[1], 'TT'))
		netlistsNr = 1

	#Dictionariy that will hold AC and OP measures of all corners
	measures = [{} for n in range(netlistsNr)]

	#If there are multiple netlists to run, runs them in parallel
	if netlistsNr > 1:
		if netlistsNr < numThreads:
			numThreads = netlistsNr

		#Launches a netlist in each thread
		for i in range(numThreads):
			t = threading.Thread(target=processNetlists, args=(q, measures))
			t.start()

		q.join()
	else:
		simObj = q.get()
		simulation(simObj, measures)

	#Writes the output file
	getOutputFile(measures)
	#Removes the simulation output files
	removeOutputFiles()
	#removeNetlists()
	#removeDesignVarIncFiles()

	#print('Time: ', time.time() - start)

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		sys.exit("The netlist and output file name have to be given as input!")
	else:
		main()

	