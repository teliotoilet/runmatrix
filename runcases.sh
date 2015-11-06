#!/bin/bash

if [ -z "$inputFile" ]; then 
    inputFile='params.sh'
fi
if [ ! -f "$inputFile" ]; then
    echo
    echo "Input file with default parameters not found: $inputFile"
    echo
    echo "STOPPING..."
    exit
fi
 
if [ -z "$casefile" ]; then
    echo 
    echo 'Need to specify $casefile environment variable'
    echo "or set it in your input file $inputFile"
    echo
    echo "STOPPING..."
    exit
fi

# - fixed/default parameters
if [ -z "$PBS_O_WORKDIR" ]; then export PBS_O_WORKDIR=`pwd`; fi
echo "Working directory: $PBS_O_WORKDIR"
echo "Sourcing parameter file: $inputFile"
. $PBS_O_WORKDIR/$inputFile

# - commands to be used
setup=$PBS_O_WORKDIR/setup.sh
liccmd='/nopt/nrel/admin/bin/lmutil lmstat -c 1999@wind-lic.nrel.gov'
 
# - environment variables for this current sweep
ORIGnodefile="$PBS_O_WORKDIR/nodelist.$PBS_JOBID"
if [ -z "$nprocs" ]; then
    # this job was run as a standalone
    if [ -z "$PBS_NUM_NODES" ]; then PBS_NUM_NODES=1; fi
    if [ -z "$PBS_NUM_PPN" ]; then PBS_NUM_PPN=1; fi
    nodes=$PBS_NUM_NODES
    cores=$PBS_NUM_PPN
    nprocs=$(($nodes*$cores))
    nodefile=$ORIGnodefile
    cat $PBS_NODEFILE | sort > $ORIGnodefile
else
    # number of cores specified by the superscript
    # - create custom node file for this set of runs
    nodefile="$PBS_O_WORKDIR/nodelist.${PBS_JOBID}_part$sweep"
    head -n $nprocs $ORIGnodefile > $nodefile
    tail -n +$((nprocs+1)) $ORIGnodefile > tmp.${PBS_JOBID}_$sweep
    mv tmp.${PBS_JOBID}_$sweep $ORIGnodefile
fi

#------------------------------------------------------------------------------
# Execution starts here

echo "Sweeping through cases defined in: $casefile"

casedir=${casefile%.*}
if [[ ${casedir##*_} == part* ]]; then
    casedir=${casedir%_part*}
fi
mkdir -p $casedir

#
# process all cases
#
echo "$PBS_O_WORKDIR started at `date`" >> $HOME/joblog
#while read -r name T H nL nH cfl; do
while eval "read -r $paramNames"; do

    cd $PBS_O_WORKDIR/$casedir

    #
    # setup new case if the subdirectory doesn't exist
    #
    echo ''
    #echo "$name : T=$T  H=$H  nL=$nL  nH=$nH  CFL=$cfl"
    echo `eval $paramInfo`
    if [ ! -d "$name" ]; then
        echo "Setting up new case $name"
        #$setup $name $T $H $nL $nH $cfl
        #$setup `eval $paramValues`
        INPUTFILE=$inputFile $setup `eval $paramValues`
    else
        if [ -f "$name/DONE" ]; then 
            echo " - done"
            continue
        fi

        echo " - case directory exists"
        if [ ! -f "$name/RUNNING" ]; then
            if [ -s "$name/log.$name" ]; then
                if [ -z "`grep 'Simulation saved' $name/log.$name`" ] || [ -n "`grep 'Terminated' $name/log.$name`" ]; then
                    echo "WARNING: Possible problem with case setup"
                    rm -v $name/log.$name # so we start over clean
                    cp -v $templateDir/$startSim $name/$name.sim
                else
                    echo "  attempting restart"
                fi
            fi
        fi
    fi

    #
    # try to run job if we have enough procs
    #
    licStr=`$liccmd -f hpcdomains | grep "Users of hpcdomains"`
    echo $licStr
    navail=`echo $licStr | awk '{print $6 - $11}'`
    while [ "$navail" -lt "$nprocs" ]; do
        echo "-- only $navail out of $nprocs licenses available --"
        sleep 15s
        licStr=`$liccmd -f hpcdomains | grep "Users of hpcdomains"`
        navail=`echo $licStr | awk '{print $6 - $11}'`
    done
    cd $name
    nprocs=$nprocs nodefile=$nodefile time sh job.pbs

done < $PBS_O_WORKDIR/$casefile


