options(scipen = 999)
library(BSDA)
warnings()

args = commandArgs(trailingOnly=TRUE)

fileNames<- list("Typical")
for(i in 0:args[4]) {
	l<-append(l, paste("crn", toString(i), sep=""))
}

for (f in fileNames){
	file1<-read.table(paste(args[1], f, ".txt", sep=""), header=TRUE)
	file2<-read.table(paste(args[2], f, ".txt", sep=""), header=TRUE)
	out<- args[3]

	for (var in colnames(file1)){
	    var1values<-file1[[var]]
	    var2values<-file2[[var]]
	    
    	abs_d<-abs((var1values-var2values)/var1values)

	    write(c(var, round(z.test(abs_d, sigma.x=sd(abs_d))$conf.int[1&2],5)), out, ncolumns=3, sep=",", append = TRUE)
	}
}
