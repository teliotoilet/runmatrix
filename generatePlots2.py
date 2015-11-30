#!/usr/bin/python
import sys
import runmatrix as mat

showfigs = True # display interactive plots

#
# SETUP RUNMATRIX
#
mat.savefigs = True # save images

# name of file in case directory containing postprocessed data, generated with post.sh and post_wave.py
#mat.postdata='post_summary.dat'
mat.postdata='post_summary2.dat' #including integrated fft error

# set parameters and defaults
# *** order in paramNames is important, should match the .txt file ***
mat.paramNames = ['name','T','H','nL','nH','cfl','halfL','dampL','extL','nInner']
mat.outputNames = ['maxerr','cumerr','lamerr','adjerr','ncells','walltime','ffterr']

mat.seriesStyles = ['r^','gs','bo']
mat.defaultStyle = 'ko'

#
# define sea state inputs | pre-calculated values (wavelength/speed) | plot ranges
#
ss0 = { 'period': 1.86, 'height': 0.08,
        'wavelength': 5.41217080198, 'wavespeed': 2.90976924838,
        'maxerr_range': (0.01,1), 'cumerr_range': (1,1e3), 'lamerr_range': (0,25)
      }
ss4 = { 'period': 4.38, 'height': 1.60,
        'wavelength': 25.0056383174, 'wavespeed': 5.70904984415,
        'maxerr_range': (1,100), 'cumerr_range': (100,1e4), 'lamerr_range': (0,15)
      }
ss5 = { 'period': 5.66, 'height': 1.20,
        'wavelength': 33.5676693735, 'wavespeed': 5.9306836349,
        'maxerr_range': (1,100), 'cumerr_range': (100,1e4), 'lamerr_range': (0,15)
      }


#-------------------------------------------------------------------------------
#
# make plots
#

if len(sys.argv) <= 1:
    casenames = ['2_ext_domain_study','2_inner_iter_study']
    print 'Using default case directories',casenames
else:
    casenames = sys.argv[1:]

db = mat.runmatrix(casenames)

# comparison of domain parameters

#db.errorPlot(ss5,
#        title='Sea state 5: damping length error',
#        xvar='dampL',xscale='linear',
#        constvar=['halfL','extL'], constval=[3,(1.5,1.75,2)],
#        seriesvar='cfl',seriesrange=(0,0.25),
#        save='2_ext_domain_study/SS5_ext_dampL_err.png')

#db.errorFftPlot(ss5,
#        title='Sea state 5: damping length error',
#        xvar='dampL',xscale='linear',
#        constvar=['halfL','nInner'], constval=[3,5],
#        seriesvar='cfl',seriesrange=(0,0.25),
#        save='2_ext_domain_study/SS5_ext_dampL_err_fft.png',
#        verbose=True)
db.errorFftPlot(ss5,
        title='Sea state 5: damping length error (extended domain)',
        xvar='dampL',xscale='linear',
        constvar=['halfL','nInner','nL','nH'], constval=[3,5,80,10],
        seriesvar='cfl',seriesrange=(0,0.25),
        save='2_ext_domain_study/SS5_ext_dampL_err_fft.png',
        verbose=True)

db.errorFftPlot(ss5,
        title='Sea state 5: inner iteration error (extend domain)',
        xvar='nInner',xscale='linear',
        constvar=['halfL','dampL','nL','nH'], constval=[3,1.5,80,10],
        seriesvar='cfl',seriesrange=(0,0.25),
        save='2_ext_domain_study/SS5_ext_nInner_err_fft.png',
        verbose=True)

if showfigs: db.show()

