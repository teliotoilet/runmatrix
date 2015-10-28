#!/usr/bin/python
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
postdata='post_summary.dat'

# general plot styles
#coarse  = 'o'
#medium  = '^'
#fine    = 's'
#vfine   = '*'
#time0   = 'r'
#time1   = 'g'
#time2   = 'b'
styles = ['^','s','o']
varnames = dict()
varnames['nL'] = 'cells per wavelength'
varnames['nH'] = 'cells per waveheight'

# pre-calculated values
ss0 = { 'period':1.86, 'height':0.08, 'wavelength':5.41217080198, 'wavespeed':2.90976924838 }
ss5 = { 'period':5.66, 'height':1.20, 'wavelength':33.5676693735, 'wavespeed':5.9306836349  }

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
        self.params = dict()
        self.excludedKeys = ['name','ncells','walltime']

    def add_case(self, name, **kwargs):
        self.cases.append( case(name, **kwargs) )
        c = self.cases[-1]
        for key in dir(c):
            if key.startswith('__') \
                    or key.endswith('err') \
                    or key in self.excludedKeys: continue
            value = getattr(c,key)
            try:
                if not value in self.params[key]:
                    self.params[key].append(value)
            except KeyError:
                self.params[key] = [value]

    def print_params(self):
        for key in self.params: print key,':',self.params[key]

    def select(self, **kwargs):
        self.selected = range(len(self.cases))
        for name,value in kwargs.items():
            Ncases = len(self.selected)
            print 'Selecting',name,'=',value,'from',Ncases,'cases'
            newselection = []
            for icase in self.selected:
                if getattr(self.cases[icase],name) == value:
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
            data[i] = getattr(self.cases[icase],col)
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
nL = np.zeros((Ncases),dtype=np.int16)
nH = np.zeros((Ncases),dtype=np.int16)
cfl = np.zeros((Ncases))
maxerr = np.zeros((Ncases))
cumerr = np.zeros((Ncases))
lamerr = np.zeros((Ncases))
adjerr = np.zeros((Ncases))
ncells = np.zeros((Ncases),dtype=np.int32)
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
db.print_params()

#===============================================================================
#
# make plots
#
def frexp10(x):# {{{
    exp = int(np.log10(x))
    return x / 10**exp, exp
def calcLogRange(vals):
    #print 'range of values:',vals

    m,e = frexp10(np.min(vals))
    #print 'xmin:',m,e
    xmin = np.floor(m)-1
    #print 'xmin:',xmin
    if xmin==0: xmin = 9*10**(e-1)
    else: xmin *= 10**e
    #print 'xmin:',xmin

    m,e = frexp10(np.max(vals))
    #print 'xmax:',m,e
    xmax = np.ceil(m)+1
    #print 'xmax:',xmax
    if xmax>=10: xmax = 2*10**(e+1)
    else: xmax *= 10**e
    #print 'xmax:',xmax

    #print 'xrange',xmin,xmax
    return (xmin,xmax)# }}}

def errorPlot(title='',ss=None,xvar='nL',constvar='nH',constval=0,seriesvar='cfl'):
    assert( constval in db.params[constvar] )
    
    # plot
    fig, [[ax0, ax1], [ax2, ax3]] = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.subplots_adjust(bottom=0.175,left=0.1,top=0.875,right=0.95)
    series = db.params[seriesvar]
    nseries = len(series)
    for i in range(nseries):
        # filter data
        cols = {'T':ss['period'], 'H':ss['height'], constvar:constval, seriesvar:series[i]}
        labelstr = seriesvar+'='+str(series[i])
        db.select(**cols)

        # get or calculate x
        #try:
        xvals = db.column(xvar)
        #except:

        ax0.loglog(xvals, db.column('maxerr'), styles[i], label=labelstr)
        ax1.loglog(xvals, db.column('cumerr'), styles[i], label=labelstr)
        ax2.semilogx(xvals, np.abs(100*db.column('lamerr')), styles[i], label=labelstr)
        ax3.loglog(xvals, db.column('adjerr'), styles[i], label=labelstr)

    # xlim
    ax0.set_xlim( calcLogRange(db.params[xvar]) )

    # axes titles
    fig.suptitle(title,fontsize=18)
    ax0.set_title('Maximum Error'); ax0.set_ylabel('maximum L2-error norm')
    ax1.set_title('Cumulative Error'); ax1.set_ylabel('cumulative L2-error norm')
    ax2.set_title('Wavelength Error'); ax2.set_ylabel('wavelength error [%]')
    ax3.set_title('Wavelength-adjusted Maximum Error'); ax3.set_ylabel('maximum L2-error norm')
    try: varname = varnames[xvar]
    except KeyError: varname = xvar
    ax2.set_xlabel(varname)
    ax3.set_xlabel(varname)

    # legend
    lines, labels = ax0.get_legend_handles_labels()
    fig.legend(lines,labels,loc='lower center',ncol=nseries) #,bbox_to_anchor=(0.,-0.02,1.,0.1)

#===============================================================================
# plot definitions here

errorPlot('Sea state 0: streamwise spacing error', ss0, \
        xvar='nL', \
        constvar='nH', constval=20,
        seriesvar='cfl')

errorPlot('Sea state 0: normal spacing error', ss0, \
        xvar='nH', \
        constvar='nL', constval=80,
        seriesvar='cfl')

plt.show()

