#!/usr/bin/python
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

#
# DEFAULTS
#
savefigs = False # save images

# name of file in case directory containing postprocessed data, generated with post.sh and post_wave.py
postdata='post_summary.dat'

# var types
dbl = np.float64 # double precision
uint = np.uint16

# set parameters and defaults
# *** order in paramNames is important, should match the .txt file ***
paramNames = ['name','T','H','nL','nH','cfl']
paramTypes = {
        'name': str,
        'T': dbl,
        'H': dbl,
        'nL': uint,
        'nH': uint,
        'cfl': dbl
        }
paramDefaults = {
        'nL': 80,
        'nH': 20,
        'cfl': 0.5
        }
paramLongNames = {
        'nL': 'cells per wavelength',
        'nH': 'cells per waveheight',
        'cfl': 'CFL'
        }
seriesStyles = ['r^','gs','bo']
defaultStyle = 'ko'

# define sea state inputs | pre-calculated values (wavelength/speed) | plot ranges
#ss_ref = { 
#        'period': 1.86, 'height': 0.08,
#        'wavelength': 5.41217080198, 'wavespeed': 2.90976924838,
#        'maxerr_range': (0.01,1), 'cumerr_range': (1,1e3), 'lamerr_range': (0,25)
#      }

#===============================================================================

# define misc global functions# {{{

def frexp10(x):
    assert( x > 0 )
    exp = int(np.log10(x))
    man = x / 10**exp
    while man < 1.0:
        man *= 10
        exp -= 1
    return man, exp
def calcLogRange(vals):
    debug = False
    if debug: print 'range of values:',vals

    m,e = frexp10(np.min(vals))
    if debug: print 'xmin:',m,e
    xmin = np.floor(m)-1
    if debug: print 'xmin:',xmin
    if xmin==0: xmin = 9*10**(e-1)
    else: xmin *= 10**e
    if debug: print 'xmin:',xmin

    m,e = frexp10(np.max(vals))
    if debug: print 'xmax:',m,e
    xmax = np.ceil(m)+1
    if debug: print 'xmax:',xmax
    if xmax>=10: xmax = 2*10**(e+1)
    else: xmax *= 10**e
    if debug: print 'xmax:',xmax

    if debug: print 'xrange',xmin,xmax
    return (xmin,xmax)
# }}}

# define structure to hold case data# {{{
class case:
    # TODO: dynamically set member variables
    def __init__(self, name, \
            T=-1, H=-1, \
            nL=-1, nH=-1, \
            cfl=-1, \
            halfL=-1, dampL=-1, \
            maxerr=-1, cumerr=-1, \
            lamerr=999, adjerr=-1, \
            ncells=-1, walltime=-1):
        self.name = name
        self.T = T
        self.H = H
        self.nL = nL
        self.nH = nH
        self.cfl = cfl
        self.halfL = halfL
        self.dampL = dampL
        self.maxerr = maxerr
        self.cumerr = cumerr
        self.lamerr = lamerr
        self.adjerr = adjerr
        self.ncells = ncells
        self.walltime = walltime
# }}}

class runmatrix:

    def __init__(self,casenames=''):
        self.cases = []
        self.selected = []
        self.params = dict()
        self.excludedKeys = ['name','ncells','walltime']
        self.caseid = dict()
        if casenames: self.read_cases(casenames)

    def add_case(self, name, **kwargs):
        self.caseid[name] = len(self.cases)
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

    def get_case(self, name):
        return self.cases[ self.caseid[name] ]

    def print_params(self,pre=''):
        for key in self.params: print pre+key,':',self.params[key]

    def select(self, **kwargs):# {{{
        if 'verbose' in kwargs.keys(): verbose = kwargs.pop('verbose')
        else: verbose = False
        self.selected = range(len(self.cases))
        for name,value in kwargs.items():
            Ncases = len(self.selected)
            newselection = []
            for icase in self.selected:
                if getattr(self.cases[icase],name) == value:
                    newselection.append(icase)
            self.selected = newselection
        if verbose: 
            sys.stdout.write('  result:')
            for i in self.selected:
                sys.stdout.write(' %s'%(self.cases[i].name))
            sys.stdout.write('\n')
        return self.selected# }}}

    def column(self, col):# {{{
        Nsel = len(self.selected)
        #data = np.zeros((Nsel))
        data = Nsel*[0]
        for i in range(Nsel):
            icase = self.selected[i]
            data[i] = getattr(self.cases[icase],col)
        try: return np.array(data)
        except ValueError: return data# }}}

    def read_cases(self,casenames):# {{{

        # initialize data
        Ncases = 0
        for casename in casenames:
            n = 0
            with open(casename+'.txt','r') as f:
                for line in f: n += 1
            print n,'cases in',casename
            Ncases += n
        print 'Building database from',Ncases,'total cases'

        data = dict()
        for param in paramNames:
            if param=='name':
                data['name'] = [ '' for i in range(Ncases) ]
                continue
            try: default = paramDefaults[param]
            except KeyError: default = -1
            data[param] = default * np.ones((Ncases), dtype=paramTypes[param])
        maxerr = np.zeros((Ncases))
        cumerr = np.zeros((Ncases))
        lamerr = np.zeros((Ncases))
        adjerr = np.zeros((Ncases))
        ncells = np.zeros((Ncases),dtype=np.uint32)
        walltime = np.zeros((Ncases))

        # read data
        icase = 0 # initial case offset
        for casename in casenames:

            fnameIn = casename + '.txt'
            fnameOut = casename + os.sep + postdata

            print 'Reading case inputs from',fnameIn
            iin = -1
            with open(fnameIn,'r') as fin:
                for line in fin:
                    line = line.split()
                    iin += 1
                    for ival in range(len(paramNames)):
                        param = paramNames[ival]
                        typ = paramTypes[param]
                        try:
                            data[param][icase+iin] = typ(line[ival])
                        except IndexError: break
                    
            print 'Reading postdata from',fnameOut
            iout = -1
            with open(fnameOut,'r') as fout:
                for line in fout:
                    line = line.split()
                    iout += 1
                    assert( line[0] == data['name'][icase+iout] )
                    maxerr[icase+iout] = float(line[1])
                    cumerr[icase+iout] = float(line[2])
                    lamerr[icase+iout] = float(line[3])
                    adjerr[icase+iout] = float(line[4])
                    ncells[icase+iout] = int(line[5])
                    walltime[icase+iout] = float(line[6])
                    
            assert(iin==iout)
            icase = iin + 1

        # fill database
        # TODO: move this to inside the read loop so we don't need extra memory
        for i in range(Ncases):
            casedata = { \
                'maxerr': maxerr[i], \
                'cumerr': cumerr[i], \
                'lamerr': lamerr[i], \
                'adjerr': adjerr[i], \
                'ncells': ncells[i], \
                'walltime': walltime[i] \
            }
            for param in paramNames:
                casedata[param] = data[param][i]

            self.add_case( **casedata )

        print 'Parameter ranges:'
        self.print_params('  ')# }}}

    # handle mouse picks in plots # {{{
    def onpick(self,event):
        line = event.artist
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        ind = event.ind
        name = line.get_label()
        print 'picked (%f,%f): figure %d > %s > %s (walltime=%d)' \
                % (xdata[ind][0],ydata[ind][0], \
                   line.figure.number, \
                   line.axes.get_title(), \
                   name, \
                   self.get_case(name).walltime \
                  )
    # }}}

    def show(self): 
        print '\n( Left-click in plots to retrieve data point info )\n'
        plt.show()

    def errorPlot(self, # {{{
            ss,                                     # sea state, must be specified
            title='',                               # sets fig.suptitle
            xvar='nL', xvarname='', xscale='',      # param name | alternate name for axes title | 'linear'
            constvar='', constval=0,                # constvar=['var1','var2',...], constval=[val1,val2,...]
            seriesvar='', seriesrange=(-9e9,9e9),   # corresponds to different plot style and legend entries
            timingcolor=False,                      # colors symbols based on log of walltime
            save='',                                # filename to output
            verbose=False):
        if title: 
            print ''
            print 'MAKING NEW PLOT "%s"'%(title)

        if not savefigs: save='' # allow global override
        
        # setup plot
        fig, [[ax0, ax1], [ax2, ax3]] = plt.subplots(nrows=2, ncols=2, sharex=True)
        if seriesvar: 
            fig.subplots_adjust(bottom=0.175,left=0.125,top=0.875,right=0.95)
            series = self.params[seriesvar]
            nseries = len(series)
        else:
            #fig.subplots_adjust(bottom=0.1,left=0.125,top=0.875,right=0.95)
            fig.subplots_adjust(bottom=0.175,left=0.125,top=0.875,right=0.95)
            nseries = 1
        xmin = 9e9; xmax = -9e9

        # select sea state and constant vars
        cols = { 'T':ss['period'], 'H':ss['height'], 'verbose':verbose }
        if constvar: 
            if isinstance(constvar, (str,unicode)):
                assert( constval in self.params[constvar] )
                cols[constvar] = constval
            else: # multiple constant parameters specified
                assert( len(constvar)==len(constval) )
                for cvar,cval in zip(constvar,constval):
                    assert( cval in self.params[cvar] )
                    cols[cvar] = cval

        if nseries > 1:
            #legendlabels = [ seriesvar+'='+str(series[i]) for i in range(nseries) ]
            legendlabels = []
            legendlines = []

        # make plot
        for i in range(nseries):

            # filter data
            if nseries > 1: 
                if series[i] < seriesrange[0] or series[i] > seriesrange[1]: 
                    if verbose: print '- Skipping series',i,':',seriesvar+'='+str(series[i]),'out of range',seriesrange
                    continue

                try:
                    legendlabels.append( paramLongNames[seriesvar] + '=' + str(series[i]) )
                except KeyError:
                    legendlabels.append( seriesvar + '=' + str(series[i]) )

                if verbose: print ' - SERIES',i,':',legendlabels[i]
                cols[seriesvar] = series[i]
                style = seriesStyles[i]
            else:
                if verbose: print ' - no series specified'
                style = defaultStyle
            if verbose: print 'selecting',cols
            selected = self.select(**cols)
            if verbose: print '  selected',len(selected),'cases to plot'

            # get or calculate x
            if xvar in self.params:
                xvals = self.column(xvar)
            else:
                formula = xvar
                if verbose: print 'Original formula:',formula
                for param in self.params:
                    paramstr = '${'+param+'}'
                    if paramstr in formula:
                        formula = formula.replace(paramstr,'self.column(\''+param+'\')')
                if '${L}' in formula: formula = formula.replace('${L}',str(ss['wavelength']))
                if '${U}' in formula: formula = formula.replace('${U}',str(ss['wavespeed']))
                if verbose: print 'Evaluated formula:',formula
                xvals = eval(formula)
            xmin = min(xmin,np.min(xvals))
            xmax = max(xmax,np.max(xvals))

            # get y
            maxerr = self.column('maxerr')
            cumerr = self.column('cumerr')
            lamerr = 100*np.abs(self.column('lamerr'))
            adjerr = self.column('adjerr')

            # make subplots
            styleargs = { 'markersize':8, 'picker':5 }
            names = self.column('name')
            if timingcolor:
                # plot each point separately
                colorscale = np.log(self.column('walltime'))
                colorscale -= np.min(colorscale)
                colorscale /= np.max(colorscale)
                for xi,err1,err2,err3,err4,c,name in \
                        zip( xvals, maxerr, cumerr, lamerr, adjerr, colorscale, names ):
                    styleargs['markerfacecolor'] = (c,0,0)
                    styleargs['markeredgecolor'] = (c,0,0)
                    styleargs['label'] = name
                    ax0.loglog(   xi, err1, style, **styleargs )
                    ax1.loglog(   xi, err2, style, **styleargs )
                    ax2.semilogx( xi, err3, style, **styleargs )
                    ax3.loglog(   xi, err4, style, **styleargs )
            else:
                for xi,err1,err2,err3,err4,name in \
                        zip( xvals, maxerr, cumerr, lamerr, adjerr, names ):
                    styleargs['label'] = name
                    ax0.loglog(   xi, err1, style, **styleargs )
                    ax1.loglog(   xi, err2, style, **styleargs )
                    ax2.semilogx( xi, err3, style, **styleargs )
                    ax3.loglog(   xi, err4, style, **styleargs )
            if xscale:
                ax0.set_xscale(xscale)
                ax1.set_xscale(xscale)
                ax2.set_xscale(xscale)
                ax3.set_xscale(xscale)

            if nseries > 1:
                legendlines.append( ax0.get_lines()[-1] )

        # end of loop over series

        # set axes limits
        if xscale=='linear':
            xr = xmax-xmin
            ax0.set_xlim( (xmin-0.2*xr, xmax+0.2*xr) )
        else:
            ax0.set_xlim( calcLogRange([xmin,xmax]) )
        if 'maxerr_range' in ss.keys():
            ax0.set_ylim( ss['maxerr_range'] )
            ax3.set_ylim( ss['maxerr_range'] )
        if 'cumerr_range' in ss.keys():
            ax1.set_ylim( ss['cumerr_range'] )
        if 'lamerr_range' in ss.keys():
            ax2.set_ylim( ss['lamerr_range'] )

        # axes titles
        fig.suptitle(title,fontsize=18)
        ax0.set_title('Maximum Error'); ax0.set_ylabel('maximum L2-error norm')
        ax1.set_title('Cumulative Error'); ax1.set_ylabel('cumulative L2-error norm')
        ax2.set_title('Wavelength Error'); ax2.set_ylabel('wavelength error [%]')
        ax3.set_title('Wavelength-adjusted Maximum Error'); ax3.set_ylabel('maximum L2-error norm')
        if xvarname:
            varname = xvarname
        else:
            try: varname = paramLongNames[xvar]
            except KeyError: varname = xvar
        ax2.set_xlabel(varname)
        ax3.set_xlabel(varname)

        # legend
        if nseries > 1:
            #lines, labels = ax0.get_legend_handles_labels()
            #fig.legend(lines,labels,loc='lower center',ncol=nseries) #,bbox_to_anchor=(0.,-0.02,1.,0.1)
            fig.legend(legendlines,legendlabels,loc='lower center',ncol=nseries)

        # hardcopy
        if save:
            fig.savefig(save)
            print 'Saved',save

        # handle picks
        fig.canvas.mpl_connect('pick_event', self.onpick)# }}}

# end of class runmatrix
