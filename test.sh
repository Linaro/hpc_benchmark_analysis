#!/usr/bin/env bash

# Horrible test driver, use something decent

# Unit tests
pytest

# "Regression" tests
echo
echo " * Regression Tests *"

out=$(python3 ./aggregate.py -p lulesh Lulesh x86_64)

# Records
logs=$(echo "$out" | grep -c Logfile)
# Perf results
inst=$(echo "$out" | grep -c instructions)
# Lulesh results
diff=$(echo "$out" | grep -c MaxRelDiff)
# Should all be the same
if [ "$logs" -ne "$inst" ] || [ "$inst" -ne "$diff" ]; then
  echo "Results don't match: [$logs] [$inst] [$diff]"
elif [ "$logs" -eq "0" ]; then
  echo "Results are all zero?"
else
  echo "Results: PASS"
fi

# Categories
cat1=$(echo "$out" | grep "^\\w" | sort -u | tr -d '[:space:]')
cat2=$(echo "$out" | grep "^  \\w" | sort -u | tr -d '[:space:]')
cat3=$(echo "$out" | grep "^    \\w" | sort -u | tr -d '[:space:]')
if [ "$cat1" == "gcc6llvm4llvm5" ] &&
   [ "$cat2" == "genericnative" ] &&
   [ "$cat3" == "1248" ]; then
  echo "Categories: PASS"
else
  echo "Categories incorrect:"
  echo "Cat 1: [$cat1]"
  echo "Cat 2: [$cat2]"
  echo "Cat 3: [$cat3]"
fi
