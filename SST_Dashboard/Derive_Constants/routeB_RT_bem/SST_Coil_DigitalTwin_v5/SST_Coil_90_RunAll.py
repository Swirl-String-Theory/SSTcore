from SST_Coil_80_ExtractEffectiveKernel_v5 import sweep
if __name__=='__main__':
    dirs=sweep([0.03,0.05,0.10],1e5,8e6,20,4,7,'weighted_gradB2','constant',0.006,1,'chord','exports/SST-Coil')
    print(dirs['base'])
