#!/bin/bash
set -e
postcmd='post_wave.py' # this should be from the fifthOrderWave git repo
outfile='post_summary.dat'

if [ -n "$1" ]; then
    inputFiles="$*"
else
    echo "USAGE: $0 [.sh parameter files] [.txt case files]"
    exit
fi


# process all files from the command line
for inputFile in $inputFiles; do
    fileext=${inputFile##*.}

    if [ "$fileext" == "sh" ]; then
        #. params.sh
        echo "Sourcing input file $inputfile"
        . $inputFile
        continue
    else
        echo "Processing cases from $inputfile"
        casefile=$inputFile
    fi
    workdir=`pwd`
    casedir=${casefile%.*}
    if [[ ${casedir##*_} == part* ]]; then
        casedir=${casedir%_part*}
    fi

    rm -f $casedir/$outfile

    echo "note: as a sanity check make sure offset in [0,lambda]"
    #while read -r name T H nL nH cfl; do
    while eval "read -r $paramNames"; do

        walltime=-1
        ncells=-1
        maxerr=-1
        cumerr=-1
        lamerr=-1
        adjerr=-1

        cd $workdir/$casedir/$name
        if [ -f "DONE" ]; then
            if [ ! -f "post.out" ]; then $postcmd &> post.out; fi
            echo "$name : `grep 'initial offset' post.out`"
            ncells=`grep 'cell count' log.$name | tail -n 1 | awk '{print $NF}'`
            walltime=`awk '{ nsec=nsec+$1 } END {print nsec}' walltime`
            maxerr=`grep 'max error' post.out | awk '{print $NF}'`
            cumerr=`grep 'cumulative error' post.out | awk '{print $NF}'`
            lamerr=`grep 'wavelength error' post.out | awk '{print $NF}'`
            adjerr=`grep 'final wavelength-corrected error' post.out | awk '{print $NF}'`
        fi

        echo $name $maxerr $cumerr $lamerr $adjerr $ncells $walltime >> $workdir/$casedir/$outfile

    done < $casefile

    echo "POST-PROCESSED RESULTS:"
    echo "name max_err cumu_err wavelength_err adjusted_err ncells walltime"
    cat $workdir/$casedir/$outfile

done
