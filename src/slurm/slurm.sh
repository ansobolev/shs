#!/bin/bash


read -d '' USAGE <<_EOF_
submit.sh, version 0.2, (c) Andrey Sobolev, 2012
Submits SIESTA job to SLURM queue

usage: -option1=value1 ... -optionX=valueX
options:
   -N=*     --nodes=*   Number of nodes needed to allocate (default: 3)
   -t=*     --time=*    Allocation time (in D-H:M:S, default: 2-0:0:0)
   -m=[i,o] --mpi=[i,o] MPI version used (i - Intel MPI, o - OpenMPI, default: i)
_EOF_
ERR_USAGE=1

ECHO_USAGE()
{
    echo "$USAGE" >&2
    exit $ERR_USAGE
}

NODES=1
TIME=1:0:0
MPI_LIST="i o"
MPI=i

for i in $*
do
        case $i in
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
    MPI_MODULE=parallel/mpi.intel/4.0.3.008
    EXE_POSTFIX=impi
    ;;
  o) 
    MPI_MODULE=parallel/mpi.openmpi/1.6-intel
    EXE_POSTFIX=ompi
    ;;
esac

# get jobname (as 3 last dirs separated by .) and projectname (the first dir in the set)
root=${PWD%/*/*/*};
base=${PWD:${#root}+1}
JOBNAME=`echo $base | sed 's/\//\./g'`
PROJNAME=`echo $JOBNAME | cut -d'.' -f1`

#make temporary job submit file
read -d '' STR << _EOF_
#!/bin/tcsh
#SBATCH --job-name Test-Lammps
#SBATCH --nodes ${NODES}
#SBATCH --time ${TIME}

#Change MPI version used
module switch parallel ${MPI_MODULE}

setenv PROGRAM python ./program.py
setenv NUM `ls stdout/${PROJNAME}.* | wc -l`

if ( ! -d stdout ) then
  mkdir stdout
endif

mpirun \${PROGRAM} > stdout/${PROJNAME}.\${NUM}.output
_EOF_

# submitting to queue
TFILE="./$(basename $0).$$.tmp"

echo "$STR" > $TFILE

sbatch $TFILE

rm $TFILE
