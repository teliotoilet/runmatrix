# FIXED PARAMETERS

#export templateDir=template
export templateDir=$PBS_O_WORKDIR/template
export startSim=start.sim

# - defaults
export d=4.0
export dsmax=1.0
export halfL=3.0

# - list of cases to run in this sweep
#   copy/paste from tank2D_convergence_study.xlsx
#   columns: name wave_period wave_height cells_per_wavelength    cells_per_waveheight    target_CFL
casefile='1_resolution_study.txt'
