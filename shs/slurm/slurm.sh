#!/bin/bash


read -d '' USAGE <<_EOF_
slurm.sh, version 0.3, (c) Andrey Sobolev, 2012-13
Submits SIESTA job to SLURM queue

usage: -option1=value1 ... -optionX=valueX
options:
   -d=*     --dir=*     Directory in which to submit job (default: current)
   -N=*     --nodes=*   Number of nodes needed to allocate (default: 3)
   -t=*     --time=*    Allocation time (in D-H:M:S, default: 3-0:0:0)
   -m=[i,o] --mpi=[i,o] MPI version used (i - Intel MPI, o - OpenMPI, default: i)
_EOF_
ERR_USAGE=1

ECHO_USAGE()
{
    echo "$USAGE" >&2
    exit $ERR_USAGE
}

DIR=
NODES=2
TIME=3-0:0:0
MPI_LIST="i o"
MPI=i

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
        -m=* | --mpi=*)
                MPI_VALUE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
                [[ $MPI_LIST =~ (^| )$MPI_VALUE($| ) ]] && MPI=$MPI_VALUE || ECHO_USAGE
                ;;
        *)
                ECHO_USAGE
                ;;
        esac
done

# get all mpi-related stuff
case $MPI in
  i)
    MPI_MODULE=parallel/mpi.intel/4.1.0.024
    EXE_POSTFIX=impi
    ;;
  o) 
    MPI_MODULE=parallel/mpi.openmpi/1.6-intel
    EXE_POSTFIX=ompi
    ;;
esac

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
read -d '' STR << _EOF_
#!/bin/tcsh
#SBATCH --job-name ${JOBNAME}
#SBATCH --nodes ${NODES}
#SBATCH --time ${TIME}

#Change MPI version used
module switch parallel ${MPI_MODULE}

setenv SIESTA ~/bin/siesta.${EXE_POSTFIX}
setenv NUM `ls stdout/${PROJNAME}.* | wc -l`

if ( ! -d stdout ) then
  mkdir stdout
endif

mpirun \${SIESTA} < ./CALC.fdf > stdout/${PROJNAME}.\${NUM}.output
_EOF_

# submitting to queue
TFILE="./$(basename $0).$$.tmp"

echo "$STR" > $TFILE

sbatch $TFILE

rm $TFILE
