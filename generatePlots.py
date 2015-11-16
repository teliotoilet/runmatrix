#!/usr/bin/python
import sys
import runmatrix as mat

showfigs = True # display interactive plots

#
# SETUP RUNMATRIX
#
mat.savefigs = True # save images

# name of file in case directory containing postprocessed data, generated with post.sh and post_wave.py
mat.postdata='post_summary.dat'

# set parameters and defaults
# *** order in paramNames is important, should match the .txt file ***
mat.paramNames = ['name','T','H','nL','nH','cfl','halfL','dampL']
mat.paramTypes = {
        'name': str,
        'T': mat.dbl,
        'H': mat.dbl,
        'nL': mat.uint,
        'nH': mat.uint,
        'cfl': mat.dbl,
        'halfL': mat.dbl,
        'dampL': mat.dbl
        }
mat.paramDefaults = {
        'nL': 80,
        'nH': 20,
        'cfl': 0.5,
        'halfL': 3.0,
        'dampL': 1.5
        }
mat.paramLongNames = {
        'nL': 'cells per wavelength',
        'nH': 'cells per waveheight',
        'cfl': 'CFL',
        'halfL': 'domain halflength',
        'dampL': 'damping length'
        }
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

if len(sys.argv) <= 1: sys.exit('specify name of studies (omit .txt extension)')
casenames = sys.argv[1:]

db = mat.runmatrix(casenames)

# reference sea state

db.errorPlot(ss0, 
        title='Sea state 0: downwave spacing error',
        xvar='nL',
        constvar='nH', constval=20,
        seriesvar='cfl',
        save='1_resolution_study/SS0_dx_err.png')

db.errorPlot(ss0, 
        title='Sea state 0: normal spacing error',
        xvar='nH',
        constvar='nL', constval=80,
        seriesvar='cfl',
        save='1_resolution_study/SS0_dz_err.png')

db.errorPlot(ss0, 
        title='Sea state 0: aspect ratio error',
        #xvar='(${H}/${nH})/(${L}/${nL})', xvarname='aspect ratio, $\Delta z/\Delta x$',
        xvar='(${L}/${nL})/(${H}/${nH})', xvarname='aspect ratio, $\Delta x/\Delta z$',
        seriesvar='cfl',
        save='1_resolution_study/SS0_ar_err.png')

db.errorPlot(ss0, 
        title='Sea state 0: temporal error',
        xvar='${T}/(${L}/${nL}/${U}*${cfl})', xvarname='Timesteps per period, $T/\Delta t$',
        seriesvar='', timingcolor=True,
        save='1_resolution_study/SS0_dt_err.png')

# nonlinear sea state

db.errorPlot(ss5,
        title='Sea state 5: downwave spacing error',
        xvar='nL',
        #constvar='nH', constval=20,
        constvar=['nH','halfL','dampL'], constval=[20,3,1.5],
        seriesvar='cfl',
        save='1_resolution_study/SS5_dx_err.png')

db.errorPlot(ss5,
        title='Sea state 5: normal spacing error',
        xvar='nH',
        #constvar='nL', constval=80,
        constvar=['nL','halfL','dampL'], constval=[80,3,1.5],
        seriesvar='cfl',
        save='1_resolution_study/SS5_dz_err.png')

db.errorPlot(ss5,
        title='Sea state 5: aspect ratio error',
        #xvar='(${H}/${nH})/(${L}/${nL})', xvarname='aspect ratio, $\Delta z/\Delta x$',
        xvar='(${L}/${nL})/(${H}/${nH})', xvarname='aspect ratio, $\Delta x/\Delta z$',
        constvar=['halfL','dampL'], constval=[3,1.5],
        seriesvar='cfl',
        save='1_resolution_study/SS5_ar_err.png')

db.errorPlot(ss5,
        title='Sea state 5: temporal error',
        xvar='${T}/(${L}/${nL}/${U}*${cfl})', xvarname='Timesteps per period, $T/\Delta t$',
        constvar=['halfL','dampL'], constval=[3,1.5],
        seriesvar='', timingcolor=True,
        save='1_resolution_study/SS5_dt_err.png')


# comparison of domain parameters

db.errorPlot(ss5,
        title='Sea state 5: damping length error',
        xvar='dampL',xscale='linear',
        #constvar='halfL', constval=3,
        #constvar=['nL','halfL'], constval=[80,3],
        #constvar=['nL','nH','halfL'], constval=[80,10,3],
        constvar=['nL','nH','halfL'], constval=[80,(10,20),3],
        seriesvar='cfl',seriesrange=(0,0.25),
        save='2_domain_study/SS5_dampL_err.png')

db.errorPlot(ss5,
        title='Sea state 5: domain length error',
        xvar='halfL',xscale='linear',
        #constvar='dampL', constval=1.5,
        #constvar=['nL','dampL'], constval=[80,1.5],
        #constvar=['nL','nH','dampL'], constval=[80,10,1.5],
        constvar=['nL','nH','dampL'], constval=[80,(10,20),1.5],
        seriesvar='cfl',seriesrange=(0,0.25),
        save='2_domain_study/SS5_halfL_err.png')


if showfigs: db.show()

