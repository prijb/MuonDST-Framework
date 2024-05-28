import FWCore.ParameterSet.Config as cms

efficiencyMC = cms.EDAnalyzer('efficiencyMC',
    nameOfOutput = cms.string('output.root'),
    isData = cms.bool(False),
    EventInfo = cms.InputTag("generator"),
    RunInfo = cms.InputTag("generator"),
    BeamSpot = cms.InputTag("offlineBeamSpot"),
    muonPacker = cms.InputTag("hltScoutingMuonPacker"),
    muonPackerVtx = cms.InputTag("hltScoutingMuonPackerVtx"),
    muonPackerNoVtx = cms.InputTag("hltScoutingMuonPackerNoVtx"),
    generatedParticles = cms.InputTag("genParticles")
)


