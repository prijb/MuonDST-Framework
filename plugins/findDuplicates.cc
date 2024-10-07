#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"

#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/RecoCandidate/interface/RecoCandidate.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"

#include "DataFormats/Scouting/interface/Run3ScoutingMuon.h"
#include "DataFormats/Scouting/interface/Run3ScoutingVertex.h"

#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/HLTReco/interface/TriggerEvent.h"

#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"

#include "L1Trigger/L1TGlobal/interface/L1TGlobalUtil.h"
#include "DataFormats/L1TGlobal/interface/GlobalAlgBlk.h"
#include "HLTrigger/HLTcore/interface/TriggerExpressionData.h"
#include "HLTrigger/HLTcore/interface/TriggerExpressionEvaluator.h"
#include "HLTrigger/HLTcore/interface/TriggerExpressionParser.h"

#include <string>
#include <iostream>
#include <vector>
#include <algorithm>
#include <memory>

#include "TLorentzVector.h"
#include "TTree.h"
#include "TH1F.h"
#include "TFile.h"



class findDuplicates : public edm::one::EDAnalyzer<edm::one::SharedResources>  {
   public:
      explicit findDuplicates(const edm::ParameterSet&);
      ~findDuplicates();

      edm::ConsumesCollector iC = consumesCollector();
      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() override;
      virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;

      edm::ParameterSet parameters;

      float MUON_MASS = 0.10566;

      //
      // --- Tokens and Handles
      //

      edm::EDGetTokenT<edm::TriggerResults> triggerBits_;
      edm::EDGetTokenT<edm::View<pat::TriggerObjectStandAlone> > triggerObjects_;
      edm::EDGetTokenT<pat::PackedTriggerPrescales>  triggerPrescales_;

      // "hltScoutingPrimaryVertexPacker" (Updated)
      edm::EDGetTokenT<edm::View<Run3ScoutingVertex> > pvToken;
      edm::Handle<edm::View<Run3ScoutingVertex> > pvs;
      // "hltScoutingMuonPackerNoVtx" (Updated)
      edm::EDGetTokenT<edm::View<Run3ScoutingMuon> > muonsNoVtxToken;
      edm::Handle<edm::View<Run3ScoutingMuon> > muonsNoVtx;
      // "hltScoutingMuonPackerVtx" (Updated)
      edm::EDGetTokenT<edm::View<Run3ScoutingMuon> > muonsVtxToken;
      edm::Handle<edm::View<Run3ScoutingMuon> > muonsVtx;
      // "hltScoutingMuonPackerNoVtx" (Updated)
      edm::EDGetTokenT<edm::View<Run3ScoutingVertex> > svsNoVtxToken;
      edm::Handle<edm::View<Run3ScoutingVertex> > svsNoVtx;
      // "hltScoutingMuonPackerVtx" (Updated)
      edm::EDGetTokenT<edm::View<Run3ScoutingVertex> > svsVtxToken;
      edm::Handle<edm::View<Run3ScoutingVertex> > svsVtx;

      // HLT
      triggerExpression::Data triggerCache_;
      std::vector<triggerExpression::Evaluator*> vtriggerSelector_;
      std::vector<std::string> vtriggerAlias_, vtriggerSelection_;

      // L1
      edm::EDGetToken algToken_;
      std::shared_ptr<l1t::L1TGlobalUtil> l1GtUtils_;
      std::vector<std::string> l1Seeds_;

      //
      // --- Variables
      //

      bool isData = false;
      bool is2024 = false;

      // Event
      Int_t event = 0;
      Int_t lumiBlock = 0;
      Int_t run = 0;

      //
      // --- Output
      //
      std::string output_filename;
      TH1F *counts;
      TFile *file_out;
      TTree *tree_out;

};

// Constructor
findDuplicates::findDuplicates(const edm::ParameterSet& iConfig) :
   triggerCache_(triggerExpression::Data(iConfig.getParameterSet("triggerConfiguration"), consumesCollector())),
   vtriggerAlias_(iConfig.getParameter<vector<string>>("triggerAlias")),
   vtriggerSelection_(iConfig.getParameter<vector<string>>("triggerSelection")),
   l1GtUtils_(nullptr)
{

   usesResource("TFileService");

   parameters = iConfig;

   vtriggerSelector_.reserve(vtriggerSelection_.size());
   for (auto const& vt:vtriggerSelection_) vtriggerSelector_.push_back(triggerExpression::parse(vt));

   algToken_ = consumes<BXVector<GlobalAlgBlk>>(iConfig.getParameter<edm::InputTag>("AlgInputTag"));
   l1GtUtils_ = std::make_shared<l1t::L1TGlobalUtil>(iConfig, consumesCollector(), l1t::UseEventSetupIn::RunAndEvent);
   l1Seeds_ = iConfig.getParameter<std::vector<std::string> >("l1Seeds");

   isData = parameters.getParameter<bool>("isData");
   is2024 = parameters.getParameter<bool>("is2024");
   pvToken = consumes<edm::View<Run3ScoutingVertex> >  (parameters.getParameter<edm::InputTag>("primaryVertexPacker"));
   muonsNoVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerNoVtx"));
   svsNoVtxToken = consumes<edm::View<Run3ScoutingVertex> >  (parameters.getParameter<edm::InputTag>("svPackerNoVtx"));
   if (is2024) {
     svsVtxToken = consumes<edm::View<Run3ScoutingVertex> >  (parameters.getParameter<edm::InputTag>("svPackerVtx"));
     muonsVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerVtx"));
   }

   counts = new TH1F("counts", "", 1, 0, 1);
}


// Destructor
findDuplicates::~findDuplicates() {
}


// beginJob (Before first event)
void findDuplicates::beginJob() {

   std::cout << "Begin Job" << std::endl;

   // Init the file and the TTree
   output_filename = parameters.getParameter<std::string>("nameOfOutput");
   file_out = new TFile(output_filename.c_str(), "RECREATE");
   tree_out = new TTree("Events", "Events");

   // Analyzer parameters
   isData = parameters.getParameter<bool>("isData");
   is2024 = parameters.getParameter<bool>("is2024");

   // TTree branches
   tree_out->Branch("event", &event, "event/I");
   tree_out->Branch("lumiBlock", &lumiBlock, "lumiBlock/I");
   tree_out->Branch("run", &run, "run/I");
}

// endJob (After event loop has finished)
void findDuplicates::endJob()
{

    std::cout << "End Job" << std::endl;
    file_out->cd();
    tree_out->Write();
    counts->Write();
    file_out->Close();

}


// fillDescriptions
void findDuplicates::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {

  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);

}

// Analyze (per event)
void findDuplicates::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {

   iEvent.getByToken(pvToken, pvs);
   iEvent.getByToken(muonsNoVtxToken, muonsNoVtx);
   iEvent.getByToken(svsNoVtxToken, svsNoVtx);
   if (is2024) {
     iEvent.getByToken(muonsVtxToken, muonsVtx);
     iEvent.getByToken(svsVtxToken, svsVtx);
   }

   // Count number of events read
   counts->Fill(0);

   // -> Event info
   event = iEvent.id().event();
   lumiBlock = iEvent.id().luminosityBlock();
   run = iEvent.id().run();
   //tree_out->Fill();

   // -> HLT
   bool passHLT = false;
   if (triggerCache_.setEvent(iEvent, iSetup)){
     auto trigAlias=vtriggerAlias_.cbegin();
     for (unsigned int i = 0; i < vtriggerSelector_.size(); i++){
       auto& vts(vtriggerSelector_.at(i));
       bool result = false;
       if (vts){
         if (triggerCache_.configurationUpdated()) vts->init(triggerCache_);
         result = (*vts)(triggerCache_);
       }
       if (result)
         passHLT = true;
       trigAlias++;
     }
   }

   passHLT = true; // hack
   if (!passHLT)
     return;

   // -> L1 seeds
   bool passL1 = false;
   l1GtUtils_->retrieveL1(iEvent, iSetup, algToken_);
   for (unsigned int i = 0; i < l1Seeds_.size(); i++){
     const auto& l1seed(l1Seeds_.at(i));
     bool l1htbit = 0;
     double prescale = -1;
     l1GtUtils_->getFinalDecisionByName(l1seed, l1htbit);
     l1GtUtils_->getPrescaleByName(l1seed, prescale);
     if (l1htbit)
       passL1 = true;
     //std::cout << l1seed << " " << l1htbit << " " << prescale << std::endl;
   }

   passL1 = true; // hack
   if (!passL1)
     return;
   
   std::vector<float> pt_values;
   for (unsigned int i = 0; i < muonsNoVtx->size(); i++) {
     const Run3ScoutingMuon& muon(muonsNoVtx->at(i));
     for (auto pt : pt_values) {
       if (std::abs(pt - muon.pt()) < 0.00000001) {
         std::cout << "El valor " << muon.pt() << " y " << pt << std::endl;
         tree_out->Fill();
       }
     }
     pt_values.push_back(muon.pt());
     //muon.pt();
   }
   //tree_out->Fill();

}

DEFINE_FWK_MODULE(findDuplicates);
