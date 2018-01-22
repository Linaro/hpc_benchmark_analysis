#!/usr/bin/env bash

CPUS=$(nproc --all)
THREADS=1

BIN="$1"
if [ ! -x "$BIN" ]; then
  echo "Can't execute $BIN"
  exit 1
fi
shift
OPTS="$*"

PERF=$(which perf)
if [ -x $PERF ] && "$PERF" -h > /dev/null; then
  PERF="$PERF stat"
else
  PERF=""
fi

while [ $THREADS -le "$CPUS" ]; do
  echo "Threads: $THREADS"
  export OMP_NUM_THREADS=$THREADS
  echo $PERF $BIN $OPTS \> "$BIN-$THREADS.log" 
  $PERF $BIN $OPTS > "$BIN-$THREADS.log" 2>&1
  THREADS=$((THREADS+THREADS))
done
unset OMP_NUM_THREADS
