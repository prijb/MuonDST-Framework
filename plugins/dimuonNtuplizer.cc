#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"

#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

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



class dimuonNtuplizer : public edm::one::EDAnalyzer<edm::one::SharedResources>  {
   public:
      explicit dimuonNtuplizer(const edm::ParameterSet&);
      ~dimuonNtuplizer();

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

      // MC
      edm::EDGetTokenT<GenEventInfoProduct>  theGenEventInfoProduct;
      edm::Handle<GenEventInfoProduct> genEvtInfo;
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

      // MC
      Float_t genWeight = 1.;

      // HLT
      TString hltNames[100] = {""};
      Bool_t hltResult[100] = {false};

      // L1
      TString l1Names[100] = {""};
      Bool_t l1Result[100] = {false};
      Float_t l1Prescale[100] = {0.0};

      Int_t nPV = 0;
      Float_t PV_x = 0;
      Float_t PV_y = 0;
      Float_t PV_z = 0;

      // Muon vertex reconstruction
      Int_t nMuonVtx = 0;
      Float_t MuonVtx_pt[200] = {0.};
      Float_t MuonVtx_eta[200] = {0.};
      Float_t MuonVtx_phi[200] = {0.};
      Int_t MuonVtx_charge[200] = {0};
      Int_t MuonVtx_nValidRecoMuonHits[200] = {0};
      Int_t MuonVtx_nRecoMuonMatchedStations[200] = {0};
      Int_t MuonVtx_nValidPixelHits[200] = {0};
      Int_t MuonVtx_type[200] = {0};
      Int_t MuonVtx_nTrackerLayersWithMeasurement[200] = {0};
      Float_t MuonVtx_trk_dxy[200] = {0};
      Float_t MuonVtx_trk_dz[200] = {0};
      Float_t MuonVtx_trk_chi2[200] = {0};
      Float_t MuonVtx_trk_ndof[200] = {0};
      Float_t MuonVtx_normalizedChi2[200] = {0};
      bool MuonVtx_hasSV[200] = {false};
      Int_t MuonVtx_bestSV[200] = {0};

      // Muon no-vertex reconstruction
      Int_t nMuonNoVtx = 0;
      Float_t MuonNoVtx_pt[200] = {0.};
      Float_t MuonNoVtx_eta[200] = {0.};
      Float_t MuonNoVtx_phi[200] = {0.};
      Int_t MuonNoVtx_charge[200] = {0};
      bool MuonNoVtx_hasSV[200] = {false};
      Int_t MuonNoVtx_bestSV[200] = {0};

      // SV from Muon no-vertex
      Int_t nSVNoVtx = 0;
      bool SVNoVtx_isValid[200] = {false};
      Float_t SVNoVtx_x[200] = {0.0};
      Float_t SVNoVtx_y[200] = {0.0};
      Float_t SVNoVtx_z[200] = {0.0};
      Float_t SVNoVtx_lxy[200] = {0.0};
      Float_t SVNoVtx_xError[200] = {0.0};
      Float_t SVNoVtx_yError[200] = {0.0};
      Float_t SVNoVtx_zError[200] = {0.0};
      Float_t SVNoVtx_chi2[200] = {0.0};
      Float_t SVNoVtx_ndof[200] = {0.0};
      Int_t SVNoVtx_nAssocMuon[200] = {0};
      Int_t SVNoVtx_index[200] = {0};
      Int_t SVNoVtx_idx1[200] = {0};
      Int_t SVNoVtx_idx2[200] = {0};
      Float_t SVNoVtx_mass[200] = {0.0};


      //
      // --- Output
      //
      std::string output_filename;
      TH1F *counts;
      TH1F *sum2Weights;
      TFile *file_out;
      TTree *tree_out;

};

// Constructor
dimuonNtuplizer::dimuonNtuplizer(const edm::ParameterSet& iConfig) :
   triggerCache_(triggerExpression::Data(iConfig.getParameterSet("triggerConfiguration"), consumesCollector())),
   vtriggerAlias_(iConfig.getParameter<vector<string>>("triggerAlias")),
   vtriggerSelection_(iConfig.getParameter<vector<string>>("triggerSelection")),
   l1GtUtils_(nullptr)
{

   usesResource("TFileService");

   parameters = iConfig;

   isData = parameters.getParameter<bool>("isData");
   is2024 = parameters.getParameter<bool>("is2024");

   if (!isData)
     theGenEventInfoProduct = consumes<GenEventInfoProduct> (parameters.getParameter<edm::InputTag>("EventInfo"));

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

   pvToken = consumes<edm::View<Run3ScoutingVertex> >  (parameters.getParameter<edm::InputTag>("primaryVertexPacker"));
   muonsNoVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerNoVtx"));
   svsNoVtxToken = consumes<edm::View<Run3ScoutingVertex> >  (parameters.getParameter<edm::InputTag>("svPackerNoVtx"));
   if (is2024) {
     svsVtxToken = consumes<edm::View<Run3ScoutingVertex> >  (parameters.getParameter<edm::InputTag>("svPackerVtx"));
     muonsVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerVtx"));
   }

   counts = new TH1F("counts", "", 1, 0, 1);
   sum2Weights = new TH1F("sum2Weights", "", 1, 0, 1);
}


// Destructor
dimuonNtuplizer::~dimuonNtuplizer() {
}


// beginJob (Before first event)
void dimuonNtuplizer::beginJob() {

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

   tree_out->Branch("genWeight", &genWeight, "genWeight/F");

   for (unsigned int iHLT=0; iHLT<vtriggerAlias_.size(); ++iHLT) {
     std::cout << hltNames[iHLT] << std::endl;
     tree_out->Branch(TString(vtriggerAlias_[iHLT]), &hltResult[iHLT]);
   }

   //for (unsigned int iL1=0; iL1<l1Seeds_.size(); ++iL1) {
   //  tree_out->Branch(TString(l1Names[iL1]), &l1Result[iL1]);
   //  std::cout << l1Names[iL1] << std::endl;
   //}

   tree_out->Branch("nPV", &nPV, "nPV/I");
   tree_out->Branch("PV_x", &PV_x, "PV_x/I");
   tree_out->Branch("PV_y", &PV_y, "PV_y/I");
   tree_out->Branch("PV_z", &PV_z, "PV_z/I");

   tree_out->Branch("nMuonVtx", &nMuonVtx, "nMuonVtx/I");
   tree_out->Branch("MuonVtx_pt", MuonVtx_pt, "MuonVtx_pt[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_eta", MuonVtx_eta, "MuonVtx_eta[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_phi", MuonVtx_phi, "MuonVtx_phi[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_charge", MuonVtx_charge, "MuonVtx_charge[nMuonVtx]/I");
   tree_out->Branch("MuonVtx_type", MuonVtx_type, "MuonVtx_type[nMuonVtx]/I");
   tree_out->Branch("MuonVtx_nValidRecoMuonHits", MuonVtx_nValidRecoMuonHits, "MuonVtx_nValidRecoMuonHits[nMuonVtx]/I");
   tree_out->Branch("MuonVtx_nRecoMuonMatchedStations", MuonVtx_nRecoMuonMatchedStations, "MuonVtx_nRecoMuonMatchedStations[nMuonVtx]/I");
   tree_out->Branch("MuonVtx_nValidPixelHits", MuonVtx_nValidPixelHits, "MuonVtx_nValidPixelHits[nMuonVtx]/I");
   tree_out->Branch("MuonVtx_nTrackerLayersWithMeasurement", MuonVtx_nTrackerLayersWithMeasurement, "MuonVtx_nTrackerLayersWithMeasurement[nMuonVtx]/I");
   tree_out->Branch("MuonVtx_trk_dxy", MuonVtx_trk_dxy, "MuonVtx_trk_dxy[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_trk_dz", MuonVtx_trk_dz, "MuonVtx_trk_dz[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_trk_chi2", MuonVtx_trk_chi2, "MuonVtx_trk_chi2[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_trk_ndof", MuonVtx_trk_ndof, "MuonVtx_trk_ndof[nMuonVtx]/F");
   tree_out->Branch("MuonVtx_normalizedChi2", MuonVtx_normalizedChi2, "MuonVtx_normalizedChi2[nMuonVtx]/F");
   //tree_out->Branch("MuonVtx_hasSV", MuonVtx_hasSV, "MuonVtx_hasSV[nMuonVtx]/I");
   //tree_out->Branch("MuonVtx_bestSV", MuonVtx_bestSV, "MuonVtx_bestSV[nMuonVtx]/I");

   tree_out->Branch("nMuonNoVtx", &nMuonNoVtx, "nMuonNoVtx/I");
   tree_out->Branch("MuonNoVtx_pt", MuonNoVtx_pt, "MuonNoVtx_pt[nMuonNoVtx]/F");
   tree_out->Branch("MuonNoVtx_eta", MuonNoVtx_eta, "MuonNoVtx_eta[nMuonNoVtx]/F");
   tree_out->Branch("MuonNoVtx_phi", MuonNoVtx_phi, "MuonNoVtx_phi[nMuonNoVtx]/F");
   tree_out->Branch("MuonNoVtx_charge", MuonNoVtx_charge, "MuonNoVtx_charge[nMuonNoVtx]/I");
   tree_out->Branch("MuonNoVtx_hasSV", MuonNoVtx_hasSV, "MuonNoVtx_hasSV[nMuonNoVtx]/I");
   tree_out->Branch("MuonNoVtx_bestSV", MuonNoVtx_bestSV, "MuonNoVtx_bestSV[nMuonNoVtx]/I");

   tree_out->Branch("nSVNoVtx", &nSVNoVtx, "nSVNoVtx/I");
   tree_out->Branch("SVNoVtx_isValid", SVNoVtx_isValid, "SVNoVtx_isValid[nSVNoVtx]/O");
   tree_out->Branch("SVNoVtx_x", SVNoVtx_x, "SVNoVtx_x[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_y", SVNoVtx_y, "SVNoVtx_y[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_z", SVNoVtx_z, "SVNoVtx_z[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_lxy", SVNoVtx_lxy, "SVNoVtx_lxy[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_xError", SVNoVtx_xError, "SVNoVtx_xError[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_yError", SVNoVtx_yError, "SVNoVtx_yError[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_zError", SVNoVtx_zError, "SVNoVtx_zError[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_chi2", SVNoVtx_chi2, "SVNoVtx_chi2[nSVNoVtx]/F");
   tree_out->Branch("SVNoVtx_ndof", SVNoVtx_ndof, "SVNoVtx_ndof[nSVNoVtx]/I");
   tree_out->Branch("SVNoVtx_index", SVNoVtx_index, "SVNoVtx_index[nSVNoVtx]/I");
   tree_out->Branch("SVNoVtx_idx1", SVNoVtx_idx1, "SVNoVtx_idx1[nSVNoVtx]/I");
   tree_out->Branch("SVNoVtx_idx2", SVNoVtx_idx2, "SVNoVtx_idx2[nSVNoVtx]/I");
   tree_out->Branch("SVNoVtx_nAssocMuon", SVNoVtx_nAssocMuon, "SVNoVtx_nAssocMuon[nSVNoVtx]/I");
   tree_out->Branch("SVNoVtx_mass", SVNoVtx_mass, "SVNoVtx_mass[nSVNoVtx]/F");

}

// endJob (After event loop has finished)
void dimuonNtuplizer::endJob()
{

    std::cout << "End Job" << std::endl;
    file_out->cd();
    tree_out->Write();
    counts->Write();
    sum2Weights->Write();
    file_out->Close();

}


// fillDescriptions
void dimuonNtuplizer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {

  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);

}

// Analyze (per event)
void dimuonNtuplizer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {

   iEvent.getByToken(pvToken, pvs);
   iEvent.getByToken(muonsNoVtxToken, muonsNoVtx);
   iEvent.getByToken(svsNoVtxToken, svsNoVtx);
   if (is2024) {
     iEvent.getByToken(muonsVtxToken, muonsVtx);
     iEvent.getByToken(svsVtxToken, svsVtx);
   }
   if (!isData)
     iEvent.getByToken(theGenEventInfoProduct, genEvtInfo);

   // Count number of events read
   counts->Fill(0);

   // -> Event info
   event = iEvent.id().event();
   lumiBlock = iEvent.id().luminosityBlock();
   run = iEvent.id().run();

   // MC gen information
   if (!isData){
       genWeight = (float) genEvtInfo->weight();
       sum2Weights->Fill(0.5, genWeight*genWeight);
   }


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

   if (!passHLT)
     return;

   std::cout << "Pasa el HLT selection" << std::endl;

   //// -> L1 seeds
   //bool passL1 = false;
   //l1GtUtils_->retrieveL1(iEvent, iSetup, algToken_);
   //for (unsigned int i = 0; i < l1Seeds_.size(); i++){
   //  const auto& l1seed(l1Seeds_.at(i));
   //  bool l1htbit = 0;
   //  double prescale = -1;
   //  l1GtUtils_->getFinalDecisionByName(l1seed, l1htbit);
   //  l1GtUtils_->getPrescaleByName(l1seed, prescale);
   //  l1Result[i] = l1htbit;
   //  l1Prescale[i] = prescale;
   //  if (l1htbit)
   //    passL1 = true;
   //  //std::cout << l1seed << " " << l1htbit << " " << prescale << std::endl;
   //}
   bool passL1=true;

   if (!passL1)
     return;
   
   std::cout << "Pasa el L1 selection" << std::endl;

   //
   // PV vertex
   //
   nPV = 0; PV_x = 0; PV_y = 0; PV_z = 0;

   nPV = pvs->size();
   if (pvs->size() > 0 && pvs->at(0).isValidVtx()) {
     PV_x = pvs->at(0).x();
     PV_y = pvs->at(0).y();
     PV_z = pvs->at(0).z();
   }

   //
   // NoVtx vertices
   //

   // Select only valid vertices
   std::vector<int> selsv_nvtx;   
   for (size_t i = 0; i < svsNoVtx->size(); i++) {
     const Run3ScoutingVertex& sv(svsNoVtx->at(i));
     //if (!sv.isValidVtx() || (sv.chi2()/sv.ndof()) > 10.)
     if (!sv.isValidVtx())
       continue;
     selsv_nvtx.push_back(i);
   }

   // Sort by chi2/ndof: Minimum chi2/ndof first
   std::sort( std::begin(selsv_nvtx), std::end(selsv_nvtx), [&](int s1, int s2){ return svsNoVtx->at(s1).chi2()/svsNoVtx->at(s1).ndof() < svsNoVtx->at(s2).chi2()/svsNoVtx->at(s2).ndof(); });

   // Save SVs and perform Muon-SV vertex association
   nSVNoVtx = 0;
   std::vector<int> assoc_nvtx;   
   int nAssocMuons;
   for (size_t i = 0; i < selsv_nvtx.size(); i++) {

     const Run3ScoutingVertex& sv(svsNoVtx->at(selsv_nvtx.at(i)));
     nAssocMuons = 0;

     // SV vertex association
     for (unsigned int j = 0; j < muonsNoVtx->size(); j++) {
       const Run3ScoutingMuon& muon(muonsNoVtx->at(j));
       if(std::find(assoc_nvtx.begin(), assoc_nvtx.end(), j) != assoc_nvtx.end()){ continue; }
       for (auto idx:muon.vtxIndx()) {
         if (idx==int(i)) {
           assoc_nvtx.push_back(j);
           nAssocMuons++;
           break;
         }
       }
       if (nAssocMuons==2)
         break;
     }
     if (!(nAssocMuons==2))
       continue;
     
     const Run3ScoutingMuon& muon1(muonsNoVtx->at(assoc_nvtx.at(assoc_nvtx.size()-2)));
     const Run3ScoutingMuon& muon2(muonsNoVtx->at(assoc_nvtx.at(assoc_nvtx.size()-1)));
     TLorentzVector mu1; mu1.SetPtEtaPhiM(muon1.pt(), muon1.eta(), muon1.phi(), MUON_MASS);
     TLorentzVector mu2; mu2.SetPtEtaPhiM(muon2.pt(), muon2.eta(), muon2.phi(), MUON_MASS);
     if ( muon1.charge()*muon2.charge() > 0.0 || mu1.DeltaR(mu2) < 0.2)
       continue; 
     SVNoVtx_idx1[nSVNoVtx] = assoc_nvtx.size()-2;
     SVNoVtx_idx2[nSVNoVtx] = assoc_nvtx.size()-1;
     SVNoVtx_index[nSVNoVtx] = selsv_nvtx.at(i);
     SVNoVtx_x[nSVNoVtx] = sv.x();
     SVNoVtx_y[nSVNoVtx] = sv.y();
     SVNoVtx_z[nSVNoVtx] = sv.z();
     SVNoVtx_lxy[nSVNoVtx] = TMath::Sqrt((sv.x()-PV_x)*(sv.x()-PV_x)+(sv.y()-PV_y)*(sv.y()-PV_y));
     SVNoVtx_xError[nSVNoVtx] = sv.xError();
     SVNoVtx_yError[nSVNoVtx] = sv.yError();
     SVNoVtx_zError[nSVNoVtx] = sv.zError();
     SVNoVtx_chi2[nSVNoVtx] = sv.chi2();
     SVNoVtx_ndof[nSVNoVtx] = sv.ndof();
     SVNoVtx_mass[nSVNoVtx] = (mu1 + mu2).M();

     nSVNoVtx++; 

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
       MuonVtx_type[nMuonVtx] = muon.type();
       MuonVtx_nValidRecoMuonHits[nMuonVtx] = muon.nValidRecoMuonHits();
       MuonVtx_nRecoMuonMatchedStations[nMuonVtx] = muon.nRecoMuonMatchedStations();
       MuonVtx_nValidPixelHits[nMuonVtx] = muon.nValidPixelHits();
       MuonVtx_nTrackerLayersWithMeasurement[nMuonVtx] = muon.nTrackerLayersWithMeasurement();
       MuonVtx_trk_dxy[nMuonVtx] = muon.trk_dxy();
       MuonVtx_trk_dz[nMuonVtx] = muon.trk_dz();
       MuonVtx_trk_chi2[nMuonVtx] = muon.trk_chi2();
       MuonVtx_trk_ndof[nMuonVtx] = muon.trk_ndof();
       MuonVtx_normalizedChi2[nMuonVtx] = muon.normalizedChi2();
       nMuonVtx++; 
     }
   }

   // NoVtx branches
   nMuonNoVtx = 0;
   //for (unsigned int i = 0; i < assoc_nvtx.size(); i++) {
   //  const Run3ScoutingMuon& muon(muonsNoVtx->at(assoc_nvtx.at(i)));
   for (unsigned int i = 0; i < muonsNoVtx->size(); i++) {
     const Run3ScoutingMuon& muon(muonsNoVtx->at(i));
     MuonNoVtx_pt[nMuonNoVtx] = muon.pt();
     MuonNoVtx_eta[nMuonNoVtx] = muon.eta();
     MuonNoVtx_phi[nMuonNoVtx] = muon.phi();
     MuonNoVtx_charge[nMuonNoVtx] = muon.charge();
     MuonNoVtx_hasSV[nMuonNoVtx] = false;
     MuonNoVtx_bestSV[nMuonNoVtx] = -1;
     for (auto vidx : muon.vtxIndx()) {
       for (int j = 0; j < nSVNoVtx; j++){
         if (vidx == SVNoVtx_index[j]) {
           MuonNoVtx_hasSV[nMuonNoVtx] = true;
           MuonNoVtx_bestSV[nMuonNoVtx] = j;
           break;
         }
       }
     }
     nMuonNoVtx++; 
   }
   // -> Fill tree
   if (nMuonVtx > 1)
       tree_out->Fill();

}

DEFINE_FWK_MODULE(dimuonNtuplizer);
