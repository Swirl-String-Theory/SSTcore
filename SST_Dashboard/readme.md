python trefoil_multisector_fitter.py exports/phi-3_1/phi3_1_transform.csv   --completion none --sectors 2 3 5 --M 150 200 300 400 --t-min 20 --t-max 35 --targets 25.18 26.75 32.80 --match-count 3 --fit-sector-weights

python trefoil_multisector_fitterv2.py  exports/phi-3_1/phi3_1_transform.csv  --completion none  --sectors 2 3 5  --M 200  --t-min 20  --t-max 35  --targets 25.18 26.75 32.80  --match-count 3  --fit-sector-weights

python trefoil_multisector_fitterv2.py  exports/phi-3_1/phi3_1_transform.csv  --completion none  --sectors 2 3 5  --M 200  --t-min 20  --t-max 35  --targets 25.18 26.75 32.80  --match-count 3



python test_monopole_from_fseries.py --batch .   --n-curve 4000    --padding 0.6   --alpha 1.0   --tube-radius 0.04 0.06 0.08 --grid 80 96 128  --beta 0.1 1.0 10.0