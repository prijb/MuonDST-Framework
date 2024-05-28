import FWCore.ParameterSet.Config as cms

ntuples = cms.EDAnalyzer('ntuplizer',
    nameOfOutput = cms.string('output.root'),
    isData = cms.bool(True),
    EventInfo = cms.InputTag("generator"),
    RunInfo = cms.InputTag("generator"),
    BeamSpot = cms.InputTag("offlineBeamSpot"),
    muonPackerVtx = cms.InputTag("hltScoutingMuonPackerVtx"),
    muonPackerNoVtx = cms.InputTag("hltScoutingMuonPackerNoVtx"),

    triggerAlias = cms.vstring(["Run3_DoubleMu3_PFScouting"]),
    triggerSelection = cms.vstring(["DST_Run3_DoubleMu3_PFScoutingPixelTracking_v*"]),
    triggerConfiguration = cms.PSet(
        hltResults            = cms.InputTag('TriggerResults','','HLT'),
        l1tResults            = cms.InputTag('','',''),
        l1tIgnoreMaskAndPrescale = cms.bool(False),
        throw                 = cms.bool(True),
        usePathStatus = cms.bool(False),
    ),
    doL1 = cms.bool(True),
    doTriggerObjects = cms.bool(False),
    AlgInputTag = cms.InputTag("gtStage2Digis"),
    l1tAlgBlkInputTag = cms.InputTag("gtStage2Digis"),
    l1tExtBlkInputTag = cms.InputTag("gtStage2Digis"),
    ReadPrescalesFromFile = cms.bool(False),
    l1Seeds = cms.vstring(["L1_DoubleMu_15_7", "L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", "L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18", "L1_DoubleMu8_SQ", "L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6", "L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4", "L1_DoubleMu4p5_SQ_OS_dR_Max1p2", "L1_DoubleMu0_Upt15_Upt7", "L1_DoubleMu0_Upt6_IP_Min1_Upt4"])

)


