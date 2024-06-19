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

      float MUON_MASS = 0.10566;

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

      // HLT
      TString hltNames[100] = {""};
      Bool_t hltResult[100] = {false};

      // L1
      TString l1Names[100] = {""};
      Bool_t l1Result[100] = {false};
      Float_t l1Prescale[100] = {0.0};

      // Muon vertex reconstruction
      Int_t nMuonVtx = 0;
      Float_t MuonVtx_pt[200] = {0.};
      Float_t MuonVtx_eta[200] = {0.};
      Float_t MuonVtx_phi[200] = {0.};
      Int_t MuonVtx_charge[200] = {0};
      Float_t MuonVtx_vtxIndx[200] = {0.};

      // Muon no-vertex reconstruction
      Int_t nMuonNoVtx = 0;
      Float_t MuonNoVtx_pt[200] = {0.};
      Float_t MuonNoVtx_eta[200] = {0.};
      Float_t MuonNoVtx_phi[200] = {0.};
      Int_t MuonNoVtx_charge[200] = {0};
      Float_t MuonNoVtx_vtxIndx[200] = {0.};

      // SV from Muon no-vertex
      Int_t nSVNoVtx = 0;
      bool SVNoVtx_isValid[200] = {false};
      Float_t SVNoVtx_x[200] = {0.0};
      Float_t SVNoVtx_y[200] = {0.0};
      Float_t SVNoVtx_z[200] = {0.0};
      Float_t SVNoVtx_xError[200] = {0.0};
      Float_t SVNoVtx_yError[200] = {0.0};
      Float_t SVNoVtx_zError[200] = {0.0};
      Float_t SVNoVtx_chi2[200] = {0.0};
      Float_t SVNoVtx_ndof[200] = {0.0};
      Int_t SVNoVtx_nAssocMuon[200] = {0};
      Int_t SVNoVtx_idx1[200] = {0};
      Int_t SVNoVtx_idx2[200] = {0};
      Float_t SVNoVtx_mass[200] = {0.0};


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
   triggerCache_(triggerExpression::Data(iConfig.getParameterSet("triggerConfiguration"), consumesCollector())),
   vtriggerAlias_(iConfig.getParameter<vector<string>>("triggerAlias")),
   vtriggerSelection_(iConfig.getParameter<vector<string>>("triggerSelection")),
   l1GtUtils_(nullptr)
{

   usesResource("TFileService");

   parameters = iConfig;

   vtriggerSelector_.reserve(vtriggerSelection_.size());
   for (auto const& vt:vtriggerSelection_) vtriggerSelector_.push_back(triggerExpression::parse(vt));
   for (unsigned int i = 0; i < l1Seeds_.size(); i++){
     const auto& l1seed(l1Seeds_.at(i));
     l1Names[i] = TString(l1seed);
   }

   algToken_ = consumes<BXVector<GlobalAlgBlk>>(iConfig.getParameter<edm::InputTag>("AlgInputTag"));
   l1GtUtils_ = std::make_shared<l1t::L1TGlobalUtil>(iConfig, consumesCollector(), l1t::UseEventSetupIn::RunAndEvent);
   l1Seeds_ = iConfig.getParameter<std::vector<std::string> >("l1Seeds");
   for (unsigned int i = 0; i < l1Seeds_.size(); i++){
     const auto& l1seed(l1Seeds_.at(i));
     l1Names[i] = TString(l1seed);
   }

   isData = parameters.getParameter<bool>("isData");
   is2024 = parameters.getParameter<bool>("is2024");
   muonsNoVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerNoVtx"));
   svsNoVtxToken = consumes<edm::View<Run3ScoutingVertex> >  (parameters.getParameter<edm::InputTag>("svPackerNoVtx"));
   if (is2024) {
     svsVtxToken = consumes<edm::View<Run3ScoutingVertex> >  (parameters.getParameter<edm::InputTag>("svPackerVtx"));
     muonsVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerVtx"));
   }

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
   is2024 = parameters.getParameter<bool>("is2024");

   // TTree branches
   tree_out->Branch("event", &event, "event/I");
   tree_out->Branch("lumiBlock", &lumiBlock, "lumiBlock/I");
   tree_out->Branch("run", &run, "run/I");

   for (unsigned int iHLT=0; iHLT<vtriggerAlias_.size(); ++iHLT) {
     std::cout << hltNames[iHLT] << std::endl;
     tree_out->Branch(TString(vtriggerAlias_[iHLT]), &hltResult[iHLT]);
   }

   for (unsigned int iL1=0; iL1<l1Seeds_.size(); ++iL1) {
     tree_out->Branch(TString(l1Names[iL1]), &l1Result[iL1]);
     std::cout << l1Names[iL1] << std::endl;
   }

   tree_out->Branch("nMuonVtx", &nMuonVtx, "nMuonVtx/I");
   tree_out->Branch("MuonVtx_pt", MuonVtx_pt, "MuonVtx_pt[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_eta", MuonVtx_eta, "MuonVtx_eta[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_phi", MuonVtx_phi, "MuonVtx_phi[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_charge", MuonVtx_charge, "MuonVtx_charge[nMuonVtx]/I");
   tree_out->Branch("MuonVtx_vtxIndx", MuonVtx_vtxIndx, "MuonVtx_vtxIndx[nMuonVtx]/I");

   tree_out->Branch("nMuonNoVtx", &nMuonNoVtx, "nMuonNoVtx/I");
   tree_out->Branch("MuonNoVtx_pt", MuonNoVtx_pt, "MuonNoVtx_pt[nMuonNoVtx]/F");
   tree_out->Branch("MuonNoVtx_eta", MuonNoVtx_eta, "MuonNoVtx_eta[nMuonNoVtx]/F");
   tree_out->Branch("MuonNoVtx_phi", MuonNoVtx_phi, "MuonNoVtx_phi[nMuonNoVtx]/F");
   tree_out->Branch("MuonNoVtx_charge", MuonNoVtx_charge, "MuonNoVtx_charge[nMuonNoVtx]/I");
   tree_out->Branch("MuonNoVtx_vtxIndx", MuonNoVtx_vtxIndx, "MuonNoVtx_vtxIndx[nMuonNoVtx]/I");

   tree_out->Branch("nSVNoVtx", &nSVNoVtx, "nSVNoVtx/I");
   tree_out->Branch("SVNoVtx_isValid", SVNoVtx_isValid, "SVNoVtx_isValid[nSVNoVtx]/O");
   tree_out->Branch("SVNoVtx_x", SVNoVtx_x, "SVNoVtx_x[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_y", SVNoVtx_y, "SVNoVtx_y[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_z", SVNoVtx_z, "SVNoVtx_z[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_xError", SVNoVtx_xError, "SVNoVtx_xError[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_yError", SVNoVtx_yError, "SVNoVtx_yError[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_zError", SVNoVtx_zError, "SVNoVtx_zError[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_chi2", SVNoVtx_chi2, "SVNoVtx_chi2[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_ndof", SVNoVtx_ndof, "SVNoVtx_ndof[nSVNoVtx]/I");
   tree_out->Branch("SVNoVtx_idx1", SVNoVtx_idx1, "SVNoVtx_idx1[nSVNoVtx]/I");
   tree_out->Branch("SVNoVtx_idx2", SVNoVtx_idx2, "SVNoVtx_idx2[nSVNoVtx]/I");
   tree_out->Branch("SVNoVtx_nAssocMuon", SVNoVtx_nAssocMuon, "SVNoVtx_nAssocMuon[nSVNoVtx]/I");
   tree_out->Branch("SVNoVtx_mass", SVNoVtx_mass, "SVNoVtx_mass[nSVNoVtx]/F");

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
       hltResult[i] = result;
       if (result)
         passHLT = true;
       trigAlias++;
     }
   }


   // -> L1 seeds
   bool passL1 = false;
   l1GtUtils_->retrieveL1(iEvent, iSetup, algToken_);
   for (unsigned int i = 0; i < l1Seeds_.size(); i++){
     const auto& l1seed(l1Seeds_.at(i));
     bool l1htbit = 0;
     double prescale = -1;
     l1GtUtils_->getFinalDecisionByName(l1seed, l1htbit);
     l1GtUtils_->getPrescaleByName(l1seed, prescale);
     l1Result[i] = l1htbit;
     l1Prescale[i] = prescale;
     if (l1htbit)
       passL1 = true;
     //std::cout << l1seed << " " << l1htbit << " " << prescale << std::endl;
   }

   
   // Vtx branches
   nMuonVtx = 0;
   if (is2024) {
     for (unsigned int i = 0; i < muonsVtx->size(); i++) {
       const Run3ScoutingMuon& muon(muonsVtx->at(i));
       MuonVtx_pt[nMuonVtx] = muon.pt();
       MuonVtx_eta[nMuonVtx] = muon.eta();
       MuonVtx_phi[nMuonVtx] = muon.phi();
       MuonVtx_charge[nMuonVtx] = muon.charge();
       nMuonVtx++; 
     }
   }

   // NoVtx branches
   nMuonNoVtx = 0;
   for (unsigned int i = 0; i < muonsNoVtx->size(); i++) {
     const Run3ScoutingMuon& muon(muonsNoVtx->at(i));
     MuonNoVtx_pt[nMuonNoVtx] = muon.pt();
     MuonNoVtx_eta[nMuonNoVtx] = muon.eta();
     MuonNoVtx_phi[nMuonNoVtx] = muon.phi();
     MuonNoVtx_charge[nMuonNoVtx] = muon.charge();
     nMuonNoVtx++; 
   }

   // NoVtx vertices
   nSVNoVtx = 0;
   for (unsigned int i = 0; i < svsNoVtx->size(); i++) {

     const Run3ScoutingVertex& sv(svsNoVtx->at(i));
     SVNoVtx_isValid[nSVNoVtx] = sv.isValidVtx();
     SVNoVtx_x[nSVNoVtx] = sv.x();
     SVNoVtx_y[nSVNoVtx] = sv.y();
     SVNoVtx_z[nSVNoVtx] = sv.z();
     SVNoVtx_xError[nSVNoVtx] = sv.xError();
     SVNoVtx_yError[nSVNoVtx] = sv.yError();
     SVNoVtx_zError[nSVNoVtx] = sv.zError();
     SVNoVtx_chi2[nSVNoVtx] = sv.chi2();
     SVNoVtx_ndof[nSVNoVtx] = sv.ndof();

     // SV vertex association
     SVNoVtx_nAssocMuon[nSVNoVtx] = 0;
     for (unsigned int j = 0; j < muonsNoVtx->size(); j++) {
       const Run3ScoutingMuon& muon(muonsNoVtx->at(j));
       for (auto idx:muon.vtxIndx()) {
         if (idx==int(i)) {
           if (SVNoVtx_nAssocMuon[nSVNoVtx]==0) {
             SVNoVtx_idx1[nSVNoVtx] = int(j);
           } else {
             SVNoVtx_idx2[nSVNoVtx] = int(j);
           }
           SVNoVtx_nAssocMuon[nSVNoVtx]++;
           break;
         }
       }
       if (SVNoVtx_nAssocMuon[nSVNoVtx]==2)
         break;
     }

     // Build the dimuon
     TLorentzVector mu1; mu1.SetPtEtaPhiM(MuonNoVtx_pt[SVNoVtx_idx1[nSVNoVtx]], MuonNoVtx_eta[SVNoVtx_idx1[nSVNoVtx]], MuonNoVtx_phi[SVNoVtx_idx1[nSVNoVtx]], MUON_MASS);
     TLorentzVector mu2; mu2.SetPtEtaPhiM(MuonNoVtx_pt[SVNoVtx_idx2[nSVNoVtx]], MuonNoVtx_eta[SVNoVtx_idx2[nSVNoVtx]], MuonNoVtx_phi[SVNoVtx_idx2[nSVNoVtx]], MUON_MASS);
     SVNoVtx_mass[nSVNoVtx] = (mu1 + mu2).M();

     /*
     if (SVNoVtx_mass[nSVNoVtx] < 0.212) {
       std::cout << "Starting muon loop within SV loop" << std::endl;
       for (unsigned int i = 0; i < muonsNoVtx->size(); i++) {
         const Run3ScoutingMuon& muon(muonsNoVtx->at(i));
         std::cout << "Muon "<< i<< " " << muon.pt() << std::endl;
       }
     }
     */

     nSVNoVtx++; 

  }

   // -> Fill tree
   if (passL1 && passHLT)
     tree_out->Fill();

}

DEFINE_FWK_MODULE(ntuplizer);
