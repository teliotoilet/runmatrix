#!/bin/bash
set -e
postcmd='post_wave.py' # this should be from the fifthOrderWave git repo
. params.sh

workdir=`pwd`
casedir=${casefile%.*}

rm -f $casedir/post_summary.dat

echo "note: as a sanity check make sure offset in [0,lambda]"
while read -r name T H nL nH cfl; do

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
        ncells=`grep 'cell count' $name.log | tail -n 1 | awk '{print $NF}'`
        walltime=`awk '{ nsec=nsec+$1 } END {print nsec}' walltime`
        maxerr=`grep 'max error' post.out | awk '{print $NF}'`
        cumerr=`grep 'cumulative error' post.out | awk '{print $NF}'`
        lamerr=`grep 'wavelength error' post.out | awk '{print $NF}'`
        adjerr=`grep 'final wavelength-corrected error' post.out | awk '{print $NF}'`
    fi

    echo $name $maxerr $cumerr $lamerr $adjerr $ncells $walltime >> $workdir/$casedir/post.dat

done < $casefile

echo "POST-PROCESSED RESULTS:"
echo "name max_err cumu_err wavelength_err adjusted_err ncells walltime"
cat $workdir/$casedir/post_summary.dat
