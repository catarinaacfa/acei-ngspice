from tkinter import *
from tkinter import filedialog, messagebox
from functools import partial

class Application:
	def __init__(self, master=None):
		self.netlistSubmitted = False
		self.testbenchSubmitted = False
		self.analyses = ['AC', 'OP', 'TRAN', 'NOISE']
		self.measuresAC = {'GDC': 'DC Gain', 'BGW': 'Gain-Bandwidth product', 'PM': 'Phase Margin', 'GAC': 'AC Gain', 'FOM': 'Figure of Merit', 'Power Supply Rejection Ratio': 'PSRR', 'Vov': 'Overdrives', 'Delta': 'Margins'}
		self.measuresOP = ['Overdrives', 'Margins']
		self.measuresTRAN = {'SR': 'Slew-Rate', 'Vov': 'Overdrives', 'Delta': 'Margins'}
		self.analysesAlreadySelected = {'OP': False, 'AC': False, 'TRAN': False, 'NOISE': False}
		self.variations = ['Decade', 'Octave', 'Linear']
		self.maxNrOfAnalyses = 4
		self.nrOfAnalyses = 0
		self.crossButtPerRow = dict()
		self.rowAnalysis = dict()
		self.widgetsPerRow = dict()

		self.font = ("Arial", "10")

		self.container1 = Frame(master)
		self.container1["pady"] = 10
		self.container1.grid(row=0, column=0)
		
		self.container2 = Frame(master)
		self.container2["padx"] = 100
		self.container2.grid(row=1, column=0)
		
		self.container3 = Frame(master)
		self.container3["padx"] = 100
		self.container3.grid(row=2, column=0)
		
		self.container4 = Frame(master)
		self.container4["pady"] = 20
		self.container4.grid(row=3, column=0)

		self.currentRow = 5
		self.container5 = self.addContainer()

		self.title = Label(self.container1, text="Netlist Builder", font=("Arial", "10", "bold")).pack()
		
		self.buttonNetlist = Button(self.container2, width=30, text="Select Netlist", font=self.font, command=self.selectNetListfile).pack()

		self.buttonTestbench = Button(self.container3, width=30, text="Select Testbench", font=self.font, command=self.selectTestbenchFile).pack()

		self.addAnalysesButton = Button(self.container4, width=12, text="Add Analyses", font=self.font, command=self.addAnalyses).pack()
		#self.addMeasuresButton = Button(self.container4, width=12, text="Add Measures", font=self.font, command=self.addMeasures).pack()
		self.buildNetlistButton = Button(self.container4, width=12, text="Get Netlist", font=self.font, command=self.buildNetlist).pack()

	def selectNetListfile(self):
		filename = filedialog.askopenfilename(initialdir=".")
		self.netList = open(filename, "r")
		self.netlistSubmitted = True
		print(self.netList.name)

	def selectTestbenchFile(self):
		filename = filedialog.askopenfilename(initialdir=".")
		self.testbench = open(filename, "r")
		self.testbenchSubmitted = True
		print(self.testbench.name)

	def addAnalyses(self):
		#if not self.netlistSubmitted:
			#messagebox.showwarning("Warning", "Netlist not selected")
		#elif not self.testbenchSubmitted:
			#messagebox.showwarning("Warning", "Testbench not selected")
		#else:
		for currAnalysis in self.analyses:
			var = Variable()
			cbox = Checkbutton(self.container5, text=currAnalysis, variable=var)
			#cbox = Checkbutton(self.container5, text=currAnalysis, variable=checkBoxes[i])
			#cbox.pack(side=TOP, anchor=W)
			cbox.grid(row=self.currentRow, column = 0)
			currAnalysisDict = dict()
			currAnalysisDict['cBoxAnalysis'] = var
			self.widgetsPerRow[currAnalysis] = currAnalysisDict
			self.appendAnalysisWidgets(currAnalysis)
			self.rowAnalysis[self.currentRow] = currAnalysis
			self.currentRow += 1
			print(currAnalysis + ' isChecked? ' + var.get())
		
	
	def appendAnalysisWidgets(self, analysis):
		if analysis == 'AC':
			self.acAnalysis()
		elif analysis == 'TRAN':
			self.tranAnalysis()
		elif analysis == 'NOISE':
			self.noiseAnalysis()
		
	def buildNetlist(self):
		#if self.netlistSubmitted and self.testbenchSubmitted:
			#print('Everything Selected')
		#elif not self.netlistSubmitted:
			#messagebox.showwarning("Warning", "Netlist not selected")
		#elif not self.testbenchSubmitted:
			#messagebox.showwarning("Warning", "Testbench not selected")
		#exit()
		for k, v in self.widgetsPerRow.items():
			print(k + ' ' + ' isChecked? ' + v.get('cBoxAnalysis').get())

	def changeAnalysis(self, *args, widget=None):
		print(widget.get())
		analysisSelected = widget.get()
		if analysisSelected != '--None--':
			alreadyExists = self.analysesAlreadySelected[analysisSelected]
			if analysisSelected == 'AC' and not alreadyExists:
				self.acAnalysis()
				self.analysesAlreadySelected[analysisSelected] = True
				self.analyses.remove('AC')
				self.rowAnalysis[self.currentRow] = 'AC'
				self.currentRow += 1
				self.nrOfAnalyses += 1
			elif analysisSelected == 'OP' and not alreadyExists:
				self.analysesAlreadySelected[analysisSelected] = True
				self.analyses.remove('OP')
				self.rowAnalysis[self.currentRow] = 'OP'
				self.currentRow += 1
				self.nrOfAnalyses += 1
			elif analysisSelected == 'TRAN' and not alreadyExists:
				self.tranAnalysis()
				self.analysesAlreadySelected[analysisSelected] = True
				self.analyses.remove('TRAN')
				self.rowAnalysis[self.currentRow] = 'TRAN'
				self.currentRow += 1
				self.nrOfAnalyses += 1
			elif analysisSelected == 'NOISE' and not alreadyExists:
				self.noiseAnalysis()
				self.analysesAlreadySelected[analysisSelected] = True
				self.analyses.remove('NOISE')
				self.rowAnalysis[self.currentRow] = 'NOISE'
				self.currentRow += 1
				self.nrOfAnalyses += 1

	def changeVariation(self, *args, widget=None, currRow=None):
		print(widget.get())
		variationSelected = widget.get()


	def acAnalysis(self):
		#Select the variation
		variationsToSelect = StringVar(self.container5)
		variationsToSelect.set(self.variations[0])

		# Link function to change dropdown
		variationsToSelect.trace('w', partial(self.changeVariation, widget=variationsToSelect, currRow=self.currentRow))
		
		self.widgetsPerRow.get('AC')['selectVariation'] = self.addDropdown(self.currentRow, 2, self.container5, variationsToSelect, self.variations)

		#Nr of points
		self.widgetsPerRow.get('AC')['nrOfPoints'] = self.addEntry(self.currentRow, 3, self.container5, 'Nr of points')

		#Start frequency
		self.widgetsPerRow.get('AC')['startFreq'] = self.addEntry(self.currentRow, 4, self.container5, 'Start freq')

		#Stop frequency
		self.widgetsPerRow.get('AC')['stopFreq'] = self.addEntry(self.currentRow, 5, self.container5, 'Stop freq')

		self.widgetsPerRow.get('AC')['measButton'] = self.addMeasButton(self.currentRow, 9)

	def tranAnalysis(self):
		#Increment
		self.widgetsPerRow.get('TRAN')['tStep'] = self.addEntry(self.currentRow, 2, self.container5, 'Tstep')

		#Final Time
		self.widgetsPerRow.get('TRAN')['fTime'] = self.addEntry(self.currentRow, 3, self.container5, 'Final Time')

		#Initial Time
		self.widgetsPerRow.get('TRAN')['iTime'] = self.addEntry(self.currentRow, 4, self.container5, 'Initial Time')

		self.widgetsPerRow.get('TRAN')['measButton'] = self.addMeasButton(self.currentRow, 9)

	def noiseAnalysis(self):
		#Output Node
		self.widgetsPerRow.get('NOISE')['outNode'] = self.addEntry(self.currentRow, 2, self.container5, 'Out Node')

		#Reference - by default is zero
		self.widgetsPerRow.get('NOISE')['ref'] = self.addEntry(self.currentRow, 3, self.container5, 'Reference')

		#Source
		self.widgetsPerRow.get('NOISE')['src'] = self.addEntry(self.currentRow, 4, self.container5, 'Source')

		#Select the variation
		variationsToSelect = StringVar(self.container5)
		variationsToSelect.set(self.variations[0])
		variationsToSelect.trace('w', partial(self.changeVariation, widget=variationsToSelect, currRow = self.currentRow))
		self.widgetsPerRow.get('NOISE')['selectVariation'] = self.addDropdown(self.currentRow, 5, self.container5, variationsToSelect, self.variations)

		#Nr of points
		self.widgetsPerRow.get('NOISE')['nrOfPoints'] = self.addEntry(self.currentRow, 6, self.container5, 'Nr of points')

		#Start frequency
		self.widgetsPerRow.get('NOISE')['startFreq'] = self.addEntry(self.currentRow, 7, self.container5, 'Start freq')

		#Stop frequency
		self.widgetsPerRow.get('NOISE')['stopFreq'] = self.addEntry(self.currentRow, 8, self.container5, 'Stop freq')

		self.widgetsPerRow.get('NOISE')['measButton'] = self.addMeasButton(self.currentRow, 9)

	def addMeasures(self, currRow=None):
		print('Going add measures')
		newWindow = Toplevel()
		self.createCheckbuttons(currRow, newWindow)

	def createCheckbuttons(self, currRow, newWindow):
		analysis = self.rowAnalysis[currRow]
		checkBoxes = dict()
		if analysis == 'AC' or analysis == 'NOISE':
			currDict = self.measuresAC
		elif analysis == 'OP':
			currDict = self.measuresOP
		elif analysis == 'TRAN':
			currDict = self.measuresTRAN

		for k,v in currDict.items():
			checkBoxes[k] = Variable()
			cbox = Checkbutton(newWindow, text=v, variable=checkBoxes[k])
			cbox.pack()

		addButton = Button(master=newWindow, width=10, text='Add')
		addButton['command'] = partial(self.parseMeasures, window=newWindow)
		addButton.pack()

	def parseMeasures(self, window):
		print('Measures Added')
		
		window.destroy()


	def addMeasButton(self, rowNr, colNr):
		addMeasuresButton = Button(self.container5, width=12, text='Add Measures', font=self.font, fg="green")
		addMeasuresButton['command'] = partial(self.addMeasures, currRow=rowNr)
		addMeasuresButton.grid(row=rowNr, column=colNr)
		return addMeasuresButton

	def destroyWidget(self, widget=None):
		print('Going to destroy widget on line = ' + str(self.crossButtPerRow.get(widget)))
		i = 0
		for w in self.widgetsPerRow.get(self.crossButtPerRow.get(widget)):
			if i == 0:
				if w.get() != '--None--':
					self.analyses.append(w.get())
				i+=1
			else:
				w.destroy()
		del self.crossButtPerRow[widget]
		widget.destroy()
		self.nrOfAnalyses -= 1

	def addContainer(self):
		newContainer = Frame()
		newContainer["pady"] = 10
		newContainer["padx"] = 50
		newContainer.grid(row=self.currentRow, column=0)
		return newContainer

	def addEntry(self, rowNr, colNr, container, placeholder=None):	
		entry = Entry(container, width=10, font=self.font)
		entry.insert(0, placeholder)
		entry.grid(row=rowNr, column=colNr)
		return entry

	def addDropdown(self, rowNr, colNr, container, stringVar, options):
		dropdown = OptionMenu(container, stringVar, *options)
		dropdown.grid(row=rowNr, column=colNr)
		return dropdown


def main():
	root = Tk()
	Application(root)
	root.mainloop()

if __name__ == "__main__":
	main()
			
