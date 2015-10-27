#!/usr/bin/python
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
postdata='post_summary.dat'

coarse  = 'o'
medium  = '^'
fine    = 's'
vfine   = '*'

#===============================================================================
# basic database

class case:
    def __init__(self, name, \
            T=-1, H=-1, \
            nL=-1, nH=-1, \
            cfl=-1, \
            maxerr=-1, cumerr=-1, \
            lamerr=999, adjerr=-1, \
            ncells=-1, walltime=-1):
        self.name = name
        self.T = T
        self.H = H
        self.nL = nL
        self.nH = nH
        self.cfl = cfl
        self.maxerr = maxerr
        self.cumerr = cumerr
        self.lamerr = lamerr
        self.adjerr = adjerr
        self.ncells = ncells
        self.walltime = walltime
        #print name,T,H,nL,nH,cfl,maxerr,cumerr,lamerr,adjerr,ncells,walltime

class runmatrix:

    def __init__(self):
        self.cases = []
        self.selected = []

    def add_case(self, name, **kwargs):
        self.cases.append( case(name, **kwargs) )

    def select(self, **kwargs):
        self.selected = range(len(self.cases))
        for name,value in kwargs.items():
            Ncases = len(self.selected)
            print 'Selecting',name,'=',value,'from',Ncases,'cases'
            newselection = []
            for icase in self.selected:
                if eval('self.cases[icase].'+name) == value:
                    newselection.append(icase)
            self.selected = newselection
        print 'result:'
        for i in self.selected:
            print ' ',self.cases[i].name

    def column(self, col):
        Nsel = len(self.selected)
        data = np.zeros((Nsel))
        for i in range(Nsel):
            icase = self.selected[i]
            data[i] = eval('self.cases[icase].'+col)
        return data

#===============================================================================

if len(sys.argv) <= 1: sys.exit('specify name of study (omit .txt extension)')
casename = sys.argv[1]

#
# initialize data
#
Ncases = 0
with open(casename+'.txt','r') as f:
    for line in f: Ncases += 1

name = [ '' for i in range(Ncases) ]
T = np.zeros((Ncases))
H = np.zeros((Ncases))
nL = np.zeros((Ncases),dtype=np.int8)
nH = np.zeros((Ncases),dtype=np.int8)
cfl = np.zeros((Ncases))
maxerr = np.zeros((Ncases))
cumerr = np.zeros((Ncases))
lamerr = np.zeros((Ncases))
adjerr = np.zeros((Ncases))
ncells = np.zeros((Ncases),dtype=np.int8)
walltime = np.zeros((Ncases))

# 
# read data
#
fname = casename + '.txt'
print 'Reading',fname
with open(fname,'r') as f:
    i = -1
    for line in f:
        line = line.split()
        i += 1
        name[i] = line[0]
        T[i] = float(line[1])
        H[i] = float(line[2])
        nL[i] = int(line[3])
        nH[i] = int(line[4])
        cfl[i] = float(line[5])
        
fname = casename + os.sep + postdata
print 'Reading',fname
with open(fname,'r') as f:
    i = -1
    for line in f:
        line = line.split()
        i += 1
        assert( line[0] == name[i] )
        maxerr[i] = float(line[1])
        cumerr[i] = float(line[2])
        lamerr[i] = float(line[3])
        adjerr[i] = float(line[4])
        ncells[i] = int(line[5])
        walltime[i] = float(line[6])
        
# 
# fill runmatrix
#
db = runmatrix()
for i in range(Ncases):
    #db.add_case( name[i] )
    db.add_case( name[i], \
            T=T[i], H=H[i], \
            nL=nL[i], nH=nH[i], \
            cfl=cfl[i], \
            maxerr=maxerr[i], cumerr=cumerr[i], \
            lamerr=lamerr[i], adjerr=adjerr[i], \
            ncells=ncells[i], walltime=walltime[i] )

#===============================================================================
#
# make plots
#

# ERROR VS CELLS/WAVELENGTH
fig, [[ax0, ax1], [ax2, ax3]] = plt.subplots(nrows=2, ncols=2, sharex=True)
fig.subplots_adjust(bottom=0.175,left=0.1,top=0.875,right=0.95)
fig.suptitle('Sea state 0: streamwise spacing error',fontsize=18)
xvar = 'nL'
xlabel = 'cells per wavelength'
styles = [coarse,medium,fine]
labels = ['ncells/H=10','ncells/H=20','ncells/H=30']

yvar = 'maxerr'
db.select(T=1.86,H=0.08,nH=10); ax0.loglog(db.column(xvar),db.column(yvar),styles[0],label=label[0])
db.select(T=1.86,H=0.08,nH=20); ax0.loglog(db.column(xvar),db.column(yvar),styles[1],label=label[1])
db.select(T=1.86,H=0.08,nH=30); ax0.loglog(db.column(xvar),db.column(yvar),styles[2],label=label[2])
ax0.set_title('Maximum Error')
ax0.set_ylabel('maximum L2-error norm')

yvar = 'cumerr'
db.select(T=1.86,H=0.08,nH=10); ax1.loglog(db.column(xvar),db.column(yvar),styles[0],label=label[0])
db.select(T=1.86,H=0.08,nH=20); ax1.loglog(db.column(xvar),db.column(yvar),styles[1],label=label[1])
db.select(T=1.86,H=0.08,nH=30); ax1.loglog(db.column(xvar),db.column(yvar),styles[2],label=label[2])
ax1.set_title('Cumulative Error')
ax1.set_ylabel('cumulative L2-error norm')

yvar = 'lamerr'
db.select(T=1.86,H=0.08,nH=10); ax2.semilogx(db.column(xvar),np.abs(100*db.column(yvar)),styles[0],label=label[0])
db.select(T=1.86,H=0.08,nH=20); ax2.semilogx(db.column(xvar),np.abs(100*db.column(yvar)),styles[1],label=label[1])
db.select(T=1.86,H=0.08,nH=30); ax2.semilogx(db.column(xvar),np.abs(100*db.column(yvar)),styles[2],label=label[2])
ax2.set_title('Wavelength Error')
ax2.set_ylabel('wavelength error [%]')

yvar = 'adjerr'
db.select(T=1.86,H=0.08,nH=10); ax3.loglog(db.column(xvar),100*db.column(yvar),styles[0],label=label[0])
db.select(T=1.86,H=0.08,nH=20); ax3.loglog(db.column(xvar),100*db.column(yvar),styles[1],label=label[1])
db.select(T=1.86,H=0.08,nH=30); ax3.loglog(db.column(xvar),100*db.column(yvar),styles[2],label=label[2])
ax3.set_title('Wavelength-adjusted Maximum Error')
ax3.set_ylabel('maximum L2-error norm')

ax2.set_xlabel(xlabel)
ax3.set_xlabel(xlabel)

lines, labels = ax0.get_legend_handles_labels()
fig.legend(lines,labels,loc='lower center',ncol=3) #,bbox_to_anchor=(0.,-0.02,1.,0.1)

# display everything
plt.show()

