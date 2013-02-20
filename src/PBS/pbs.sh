#!/bin/bash

read -d '' USAGE <<_EOF_
pbs.sh, version 0.1, (c) Andrey Sobolev, 2013
Submits SIESTA job to PBS queue

usage: -option1=value1 ... -optionX=valueX
options:
   -d=*     --dir=*     Directory in which to submit job (default: current)
   -N=*     --nodes=*   Number of nodes needed to allocate (default: 3)
   -t=*     --time=*    Allocation time (in H:M:S, default: 48:0:0)
_EOF_
ERR_USAGE=1

ECHO_USAGE()
{
    echo "$USAGE" >&2
    exit $ERR_USAGE
}

DIR=
NODES=1
TIME=48:0:0

for i in $*
do
        case $i in
        -d=* | --dir=*)
                DIR=`echo $i | sed 's/[-a-zA-Z0-9]*=//'` && DIR=${DIR}
                ;;
        -N=* | --nodes=*)
                NODES=`echo $i | sed 's/[-a-zA-Z0-9]*=//'` && NODES=${NODES}
                ;;
        -t=* | --time=*)
                TIME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'` && TIME=${TIME}
                ;;
        *)
                ECHO_USAGE
                ;;
        esac
done

# if DIR is set, then cd there
if [ -z $DIR ]; then
  DIR=$PWD
else
  cd $DIR
fi

# get jobname (as 3 last dirs separated by .) and projectname (the first dir in the set)
root=${DIR%/*/*/*};
base=${DIR:${#root}+1}
JOBNAME=`echo $base | sed 's/\//\./g'`
PROJNAME=`echo $JOBNAME | cut -d'.' -f1`
#make temporary job submit file
read -d '' STR <<_EOF_
#!/bin/tcsh

#PBS -N ${JOBNAME}
#PBS -l nodes=${NODES}:ppn=12,walltime=${TIME}
#PBS -S /bin/sh
#PBS -V

#cd to the working directory
cd ${DIR}

setenv SIESTA ~/bin/siesta
setenv NUM `ls stdout/${PROJNAME}.* | wc -l`
setenv NNODES \`cat \$PBS_NODEFILE | wc -l\`

if ( ! -d stdout ) then
  mkdir stdout
endif

mpirun -n ${NNODES} \${SIESTA} < ./CALC.fdf >& stdout/${PROJNAME}.\${NUM}.output

_EOF_
# submitting to queue
TFILE="./$(basename $0).$$.tmp"

echo "$STR" > $TFILE

qsub $TFILE

rm $TFILE
