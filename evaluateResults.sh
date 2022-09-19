#!/bin/sh

# Running evaluation with different collars - 0.25 s down to 0 with 0.05 s intervals
echo "perl md-eval-v21.pl -m -afc -c 0.25 -r "$3" -s "$1$2".rttm > "$1"NISTEvaluation_2_5.txt"
perl md-eval-v21.pl -m -afc -c 0.25 -r $3 -s $1$2.rttm > $1NISTEvaluation_2_5.txt
perl md-eval-v21.pl -m -afc -c 0.20 -r $3 -s $1$2.rttm > $1NISTEvaluation_2_0.txt
perl md-eval-v21.pl -m -afc -c 0.15 -r $3 -s $1$2.rttm > $1NISTEvaluation_1_5.txt
perl md-eval-v21.pl -m -afc -c 0.10 -r $3 -s $1$2.rttm > $1NISTEvaluation_1_0.txt
perl md-eval-v21.pl -m -afc -c 0.05 -r $3 -s $1$2.rttm > $1NISTEvaluation_0_5.txt
perl md-eval-v21.pl -m -afc -r $3 -s $1$2.rttm > $1NISTEvaluation_0_0.txt

