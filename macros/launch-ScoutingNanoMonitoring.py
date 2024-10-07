import ROOT
import os

inputdir = '/store/user/pinkaew/scouting_nano_dev_v0p6_golden/ScoutingPFMonitor/'
era = 'Run2024G'
# DST_PFScouting_DoubleMuon, DST_PFScouting_DoubleEG, DST_PFScouting_JetHT, DST_PFScouting_SingleMuon
hlt = 'DST_PFScouting_ZeroBias'
hlt = 'none'
os.system(f'xrdfs root://hip-cms-se.csc.fi ls {inputdir} > temp_level1.txt')
with open(f'temp_level1.txt', 'r') as file1:
    level1 = file1.readlines()
    for l1_,l1 in enumerate(level1):
        if era not in l1: continue
        print(f'xrdfs root://hip-cms-se.csc.fi ls {l1[:-1]} > temp_level2.txt')
        os.system(f'xrdfs root://hip-cms-se.csc.fi ls {l1[:-1]} > temp_level2.txt')
        with open(f'temp_level2.txt', 'r') as file:
            l2 = file.read()
            print(f'xrdfs root://hip-cms-se.csc.fi ls {l2[:-1]} > temp_level3.txt')
            os.system(f'xrdfs root://hip-cms-se.csc.fi ls {l2[:-1]} > temp_level3.txt')
        with open(f'temp_level3.txt', 'r') as file:
            level3 = file.readlines() 
        for l3_,l3 in enumerate(level3): # 0000/ 0001/ 0002... level
            tag = '%s_%s_%s_%s'%(era, hlt, str(l1_), str(l3_))
            shfile_temp = open('submitNanoScoutingMonitoringAnalysis.sh', 'r')
            shtext_temp = shfile_temp.read()
            shtext = shtext_temp.replace('TTAG', tag)
            print(l3)
            shtext = shtext.replace('IINDIR', l3)
            shtext = shtext.replace('HHLT', hlt)
            shfile_temp.close()
            with open('submitNanoScoutingMonitoringAnalysis_%s_%s.sh'%(str(l1_), str(l3_)), 'w') as shfile:
                shfile.write(shtext)
            os.system('sh submitNanoScoutingMonitoringAnalysis_%s_%s.sh'%(str(l1_), str(l3_)))
            os.system('rm submitNanoScoutingMonitoringAnalysis_%s_%s.sh'%(str(l1_), str(l3_)))
        break
os.system('rm temp_level1.txt')
os.system('rm temp_level2.txt')
os.system('rm temp_level3.txt')
