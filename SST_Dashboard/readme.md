python trefoil_multisector_fitter.py exports/phi-3_1/phi3_1_transform.csv   --completion none --sectors 2 3 5 --M 150 200 300 400 --t-min 20 --t-max 35 --targets 25.18 26.75 32.80 --match-count 3 --fit-sector-weights

python trefoil_multisector_fitterv2.py  exports/phi-3_1/phi3_1_transform.csv  --completion none  --sectors 2 3 5  --M 200  --t-min 20  --t-max 35  --targets 25.18 26.75 32.80  --match-count 3  --fit-sector-weights

python trefoil_multisector_fitterv2.py  exports/phi-3_1/phi3_1_transform.csv  --completion none  --sectors 2 3 5  --M 200  --t-min 20  --t-max 35  --targets 25.18 26.75 32.80  --match-count 3

python oriented_link_scoresv2.py . --only TL3.3 --json-out tl33_scores.json
python oriented_link_scoresv2.py . --only 6.3.3 --json-out 6.3.3_scores.json

python test_monopole_from_fseries.py --batch .   --n-curve 4000    --padding 0.6   --alpha 1.0   --tube-radius 0.04 0.06 0.08 --grid 80 96 128  --beta 0.1 1.0 10.0

SST_Dashboard
python trefoil_multisector_week12.py exports/phi-3_1/phi3_1_transform.csv --M-values 100,150,200,250,300,400 --seeds 1001,1002,1003,1004,1005 --windows 20:35,23:34,24:33 --target-sets 25.18|26.75|32.80|25.18|26.75 --lambda-extra 0.5 --sigma-extra 0.05 --lambda-reg 0.01 --plots