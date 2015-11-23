#!/bin/bash
set -e
postcmd='post_wave_fft.py' # this should be from the fifthOrderWave git repo
postoutput='post_fft.out'
outputtimes='0 0.5 1.0' # fraction of simulation time to perform FFT at
outfile='post_fft_summary.dat'

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
        echo "Sourcing input file $inputFile"
        . $inputFile
        continue
    else
        echo "Processing cases from $inputFile"
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

        highfreqerr=-1

        cd $workdir/$casedir/$name
        if [ -f "DONE" ]; then
            if [ ! -f "$postoutput" ]; then 
                postargs=""
                for frac in $outputtimes; do
                    postargs="$postargs `echo "scale=2; $T * $frac" | bc`"
                done
                echo $postcmd $postargs
                $postcmd $postargs &> $postoutput
            fi
            line=`tail -n 1 $postoutput`
            echo "$name : $line"
            highfreqerr=`echo $line | awk '{print $NF}'`
        fi

        echo $name $highfreqerr >> $workdir/$casedir/$outfile

    done < $casefile

    echo "POST-PROCESSED RESULTS:"
    echo "name high_freq_err"
    cat $workdir/$casedir/$outfile

done
