param(
    [string]$Ideal = "ideal.txt",
    [string]$OutRoot = "outputs_routeB_BEM_v14_multirun_extensive"
)

Write-Host "Running BEMv14 extensive staged multigrid suite"
Write-Host "ideal:   $Ideal"
Write-Host "outroot: $OutRoot"

python routeB_RT_bem_v14_multirun_grids.py `
  --ideal $Ideal `
  --outdir "${OutRoot}_A_probe" `
  --grid-suite-json BEMv14_suite_stageA_probe.json `
  --length-samples 8000 `
  --subrun-timeout 600 `
  --grid-run-timeout 900 `
  --multirun-timeout 7200

python routeB_RT_bem_v14_multirun_grids.py `
  --ideal $Ideal `
  --outdir "${OutRoot}_B_production" `
  --grid-suite-json BEMv14_suite_stageB_production.json `
  --length-samples 16000 `
  --subrun-timeout 1200 `
  --grid-run-timeout 1800 `
  --multirun-timeout 21600

python routeB_RT_bem_v14_multirun_grids.py `
  --ideal $Ideal `
  --outdir "${OutRoot}_C_stress" `
  --grid-suite-json BEMv14_suite_stageC_stress.json `
  --subrun-timeout 1800 `
  --grid-run-timeout 3600 `
  --multirun-timeout 43200

Write-Host "Stage A/B/C complete. Only run Stage D if A/B/C agree."
