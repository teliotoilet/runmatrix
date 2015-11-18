#!/bin/bash

rsync -aPv equon@peregrine:/scratch/equon/`this`/template/* template/ 2>/dev/null

#scp equon@peregrine:/scratch/equon/`this`/{*.sh*,*.txt,*.pbs} .
rsync -aPv equon@peregrine:/scratch/equon/`this`/*.sh . 2>/dev/null
rsync -aPv equon@peregrine:/scratch/equon/`this`/*.txt . 2>/dev/null
rsync -aPv equon@peregrine:/scratch/equon/`this`/*.pbs . 2>/dev/null

