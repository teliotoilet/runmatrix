# FIXED PARAMETERS

# templateDir=template
templateDir=$PBS_O_WORKDIR/template
startSim=start.sim

# - defaults
name='test'
T=1.86
H=0.08
nL=80
nH=20
cfl=0.5
d=4.0
dsmax=1.0
halfL=3.0
dampL=1.5
width=1.0

# - list of cases to run in this sweep
#   copy/paste from tank2D_convergence_study.xlsx
#   columns: name wave_period wave_height cells_per_wavelength    cells_per_waveheight    target_CFL    domain_length  beach_length
paramNames='name T H nL nH cfl halfL dampL'



#######################################################################################
#
# setup param strings
#
#paramValueNames='$name $T $H $nL $nH $cfl'
paramValueNames=""
paramInfoString=""
for p in $paramNames; do
    paramValueNames="$paramValueNames \$$p"
    paramInfoString="$paramInfoString  $p=\$$p"
done
paramValues="echo $paramValueNames"
paramInfo="echo $paramInfoString"

