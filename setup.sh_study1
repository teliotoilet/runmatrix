#!/bin/bash
set -e
. $PBS_O_WORKDIR/params.sh

T="$1"
H="$2"
nL="$3"
nH="$4"
cfl="$5"
name="$6"
if [ -z "$T" -o -z "$H" -o -z "$nL" -o -z "$nH" -o -z "$cfl" ]; then
    echo "USAGE: $0 wavePeriod waveHeight ncells_L ncells_H targetCFL [caseName]"
    exit
fi
if [ -z "$name" ]; then name="test"; fi

if [ -d "$name" ]; then
    echo "Run directory with name '$name' already exists, aborting"
    exit
fi

echo "Input wave period = $T"
echo "Input wave height = $H"
echo "Input cells/wavelength = $nL"
echo "Input cells/waveheight = $nH"
echo "Input target CFL = $cfl"

L=`fenton1985.py $T $H lambda`
echo "Calculated wave length = $L"
U=`fenton1985.py $T $H $L umean`
echo "Calculated mean wave speed = $U"

#macroName=${name}_setup
#echo "Generating ${macroName}.java"
macroName=setupSim
cp $templateDir/template.java ${macroName}.java
sed -i "s/<<caseName>>/$name/" ${macroName}.java
sed -i "s|<<curDir>>|`pwd`/$name|" ${macroName}.java # use '|' instead of '/' to avoid problem with path name
sed -i "s/<<H>>/$H/" ${macroName}.java
sed -i "s/<<T>>/$T/" ${macroName}.java
sed -i "s/<<L>>/$L/" ${macroName}.java
sed -i "s/<<U>>/$U/" ${macroName}.java
sed -i "s/<<d>>/$d/" ${macroName}.java
sed -i "s/<<halfL>>/$halfL/" ${macroName}.java
sed -i "s/<<nL>>/$nL/" ${macroName}.java
sed -i "s/<<nH>>/$nH/" ${macroName}.java
sed -i "s/<<ds0>>/$dsmax/" ${macroName}.java
sed -i "s/<<cfl>>/$cfl/" ${macroName}.java

mkdir $name
mv -v ${macroName}.java $name/
cp -v $templateDir/$startSim $name/${name}.sim
#cp -v $templateDir/run.sh $name/
#cp -v $templateDir/job.pbs $name/

echo "#!/bin/bash" > $name/job.pbs
grep "#PBS" $PBS_O_WORKDIR/job.pbs >> $name/job.pbs
cat $templateDir/job.pbs.tmp >> $name/job.pbs

echo "Setup complete."
