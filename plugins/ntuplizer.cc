#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"

#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Scouting/interface/Run3ScoutingMuon.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/RecoCandidate/interface/RecoCandidate.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"

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



class ntuplizer : public edm::one::EDAnalyzer<edm::one::SharedResources>  {
   public:
      explicit ntuplizer(const edm::ParameterSet&);
      ~ntuplizer();

      edm::ConsumesCollector iC = consumesCollector();
      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() override;
      virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;

      edm::ParameterSet parameters;

      //
      // --- Tokens and Handles
      //

      edm::EDGetTokenT<edm::TriggerResults> triggerBits_;
      edm::EDGetTokenT<edm::View<pat::TriggerObjectStandAlone> > triggerObjects_;
      edm::EDGetTokenT<pat::PackedTriggerPrescales>  triggerPrescales_;

      // "hltScoutingMuonPackerNoVtx" (Updated)
      edm::EDGetTokenT<edm::View<Run3ScoutingMuon> > muonsNoVtxToken;
      edm::Handle<edm::View<Run3ScoutingMuon> > muonsNoVtx;
      // "hltScoutingMuonPackerVtx" (Updated)
      edm::EDGetTokenT<edm::View<Run3ScoutingMuon> > muonsVtxToken;
      edm::Handle<edm::View<Run3ScoutingMuon> > muonsVtx;

      edm::EDGetToken algToken_;
      std::shared_ptr<l1t::L1TGlobalUtil> l1GtUtils_;
      std::vector<std::string> l1Seeds_;

      //
      // --- Variables
      //

      bool isData = false;

      // Event
      Int_t event = 0;
      Int_t lumiBlock = 0;
      Int_t run = 0;

      TString l1Names[10] = {""};
      bool l1Result[10] = {false};
      float l1Prescale[10] = {0.0};

      // Muon vertex reconstruction
      Int_t nMuonVtx = 0;
      Float_t MuonVtx_pt[200] = {0.};
      Float_t MuonVtx_eta[200] = {0.};
      Float_t MuonVtx_phi[200] = {0.};

      // Muon no-vertex reconstruction
      Int_t nMuonNoVtx = 0;
      Float_t MuonNoVtx_pt[200] = {0.};
      Float_t MuonNoVtx_eta[200] = {0.};
      Float_t MuonNoVtx_phi[200] = {0.};
      //
      // --- Output
      //
      std::string output_filename;
      TH1F *counts;
      TFile *file_out;
      TTree *tree_out;

};

// Constructor
ntuplizer::ntuplizer(const edm::ParameterSet& iConfig) :
   l1GtUtils_(nullptr)
{

   usesResource("TFileService");

   parameters = iConfig;

   algToken_ = consumes<BXVector<GlobalAlgBlk>>(iConfig.getParameter<edm::InputTag>("AlgInputTag"));
   l1GtUtils_ = std::make_shared<l1t::L1TGlobalUtil>(iConfig, consumesCollector(), l1t::UseEventSetupIn::RunAndEvent);
   l1Seeds_ = iConfig.getParameter<std::vector<std::string> >("l1Seeds");
   for (unsigned int i = 0; i < l1Seeds_.size(); i++){
     const TString& l1seed(l1Seeds_.at(i));
     l1Names[i] = TString(l1seed);
   }

   isData = parameters.getParameter<bool>("isData");
   muonsVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerVtx"));
   muonsNoVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerNoVtx"));

   counts = new TH1F("counts", "", 1, 0, 1);
}


// Destructor
ntuplizer::~ntuplizer() {
}


// beginJob (Before first event)
void ntuplizer::beginJob() {

   std::cout << "Begin Job" << std::endl;

   // Init the file and the TTree
   output_filename = parameters.getParameter<std::string>("nameOfOutput");
   file_out = new TFile(output_filename.c_str(), "RECREATE");
   tree_out = new TTree("Events", "Events");

   // Analyzer parameters
   isData = parameters.getParameter<bool>("isData");

   // TTree branches
   tree_out->Branch("event", &event, "event/I");
   tree_out->Branch("lumiBlock", &lumiBlock, "lumiBlock/I");
   tree_out->Branch("run", &run, "run/I");

   for (unsigned int iL1=0; iL1<l1Seeds_.size(); ++iL1) {
    tree_out->Branch(TString(l1Names[iL1]), l1Result[iL1]);
    //std::cout << TString(l1Names[iL1]) << std::endl;
   }

   tree_out->Branch("nMuonVtx", &nMuonVtx, "nMuonVtx/I");
   tree_out->Branch("MuonVtx_pt", MuonVtx_pt, "MuonVtx_pt[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_eta", MuonVtx_eta, "MuonVtx_eta[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_phi", MuonVtx_phi, "MuonVtx_phi[nMuonVtx]/F");

   tree_out->Branch("nMuonNoVtx", &nMuonNoVtx, "nMuonNoVtx/I");
   tree_out->Branch("MuonNoVtx_pt", MuonNoVtx_pt, "MuonNoVtx_pt[nMuonNoVtx]/F");
   tree_out->Branch("MuonNoVtx_eta", MuonNoVtx_eta, "MuonNoVtx_eta[nMuonNoVtx]/F");
   tree_out->Branch("MuonNoVtx_phi", MuonNoVtx_phi, "MuonNoVtx_phi[nMuonNoVtx]/F");

}

// endJob (After event loop has finished)
void ntuplizer::endJob()
{

    std::cout << "End Job" << std::endl;
    file_out->cd();
    tree_out->Write();
    counts->Write();
    file_out->Close();

}


// fillDescriptions
void ntuplizer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {

  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);

}

// Analyze (per event)
void ntuplizer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {

   iEvent.getByToken(muonsNoVtxToken, muonsNoVtx);
   iEvent.getByToken(muonsVtxToken, muonsVtx);

   // Count number of events read
   counts->Fill(0);

   // -> Event info
   event = iEvent.id().event();
   lumiBlock = iEvent.id().luminosityBlock();
   run = iEvent.id().run();

   l1GtUtils_->retrieveL1(iEvent, iSetup, algToken_);
   //for (auto const& l1seed:l1Seeds){
   for (unsigned int i = 0; i < l1Seeds_.size(); i++){
     const auto& l1seed(l1Seeds_.at(i));
     bool l1htbit = 0;
     double prescale = -1;
     l1GtUtils_->getFinalDecisionByName(l1seed, l1htbit);
     l1GtUtils_->getPrescaleByName(l1seed, prescale);
     l1Result[i] = l1htbit;
     l1Prescale[i] = prescale;
     std::cout << l1seed << " " << l1htbit << " " << prescale << std::endl;
   }

   // Vtx branches
   nMuonVtx = 0;
   for (unsigned int i = 0; i < muonsVtx->size(); i++) {
     const Run3ScoutingMuon& muon(muonsVtx->at(i));
     MuonVtx_pt[nMuonVtx] = muon.pt();
     MuonVtx_eta[nMuonVtx] = muon.eta();
     MuonVtx_phi[nMuonVtx] = muon.phi();
     nMuonVtx++; 
   }

   // NoVtx branches
   nMuonNoVtx = 0;
   for (unsigned int i = 0; i < muonsNoVtx->size(); i++) {
     const Run3ScoutingMuon& muon(muonsNoVtx->at(i));
     MuonNoVtx_pt[nMuonNoVtx] = muon.pt();
     MuonNoVtx_eta[nMuonNoVtx] = muon.eta();
     MuonNoVtx_phi[nMuonNoVtx] = muon.phi();
     nMuonNoVtx++; 
   }

   // -> Fill tree
   tree_out->Fill();

}

DEFINE_FWK_MODULE(ntuplizer);
