import FWCore.ParameterSet.Config as cms

ntuples = cms.EDAnalyzer('ntuplizer',
    nameOfOutput = cms.string('output.root'),
    isData = cms.bool(True),
    EventInfo = cms.InputTag("generator"),
    RunInfo = cms.InputTag("generator"),
    BeamSpot = cms.InputTag("offlineBeamSpot"),
    displacedGlobalCollection = cms.InputTag("displacedGlobalMuons"),
    displacedStandAloneCollection = cms.InputTag("displacedStandAloneMuons"),
    displacedMuonCollection = cms.InputTag("slimmedDisplacedMuons")
)


