import FWCore.ParameterSet.Config as cms

efficiencyMC = cms.EDAnalyzer('efficiencyMC',
    nameOfOutput = cms.string('output.root'),
    isData = cms.bool(False),
    EventInfo = cms.InputTag("generator"),
    RunInfo = cms.InputTag("generator"),
    #BeamSpot = cms.InputTag("offlineBeamSpot"),
    muonPacker = cms.InputTag("hltScoutingMuonPacker"),
    muonPackerVtx = cms.InputTag("hltScoutingMuonPackerVtx"),
    muonPackerNoVtx = cms.InputTag("hltScoutingMuonPackerNoVtx"),
    svPackerVtx = cms.InputTag("hltScoutingMuonPackerVtx", "displacedVtx", "HLT"),
    svPackerNoVtx = cms.InputTag("hltScoutingMuonPackerNoVtx", "displacedVtx", "HLT"),
    generatedParticles = cms.InputTag("genParticles"),
    triggerConfiguration = cms.PSet(
        hltResults            = cms.InputTag('TriggerResults','','HLTX'),
        l1tResults            = cms.InputTag('','',''),
        l1tIgnoreMaskAndPrescale = cms.bool(False),
        throw                 = cms.bool(True),
        usePathStatus = cms.bool(False),
    )
)


