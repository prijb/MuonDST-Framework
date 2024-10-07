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



class analyzer : public edm::one::EDAnalyzer<edm::one::SharedResources>  {
   public:
      explicit analyzer(const edm::ParameterSet&);
      ~analyzer();

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
      std::vector<std::string> DoubleMu_l1Seeds_;
      std::vector<std::string> SingleMu_l1Seeds_;

      //
      // --- Variables
      //

      bool verbose = false;
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
      TString DoubleMu_l1Names[100] = {""};
      Bool_t DoubleMu_l1Result[100] = {false};
      Float_t DoubleMu_l1Prescale[100] = {0.0};

      TString SingleMu_l1Names[100] = {""};
      Bool_t SingleMu_l1Result[100] = {false};
      Float_t SingleMu_l1Prescale[100] = {0.0};

      //
      // --- Output
      //
      std::string output_filename;
      TH1F *counts;

      // DoubleMuon
      std::vector<TH1F*> h_DoubleMu_MuonNoVtx_pt;
      std::vector<TH1F*> h_DoubleMu_MuonNoVtx_eta;
      std::vector<TH1F*> h_DoubleMu_MuonNoVtx_phi;
      std::vector<TH1F*> h_DoubleMu_SVNoVtx_mass;

      // SingleMuon
      std::vector<TH1F*> h_SingleMu_MuonVtx_pt;
      std::vector<TH1F*> h_SingleMu_MuonVtx_eta;
      std::vector<TH1F*> h_SingleMu_MuonVtx_phi;

      TH1F* h_ZeroBias_MuonNoVtx_pt;
      TH1F* h_ZeroBias_MuonNoVtx_eta;
      TH1F* h_ZeroBias_MuonNoVtx_phi;
      TH1F* h_ZeroBias_SVNoVtx_mass;
      TH1F* h_ZeroBias_MuonVtx_pt;
      TH1F* h_ZeroBias_MuonVtx_eta;
      TH1F* h_ZeroBias_MuonVtx_phi;
      TH1F* h_ZeroBias_SVVtx_mass;
      TH1F* h_ZeroBias_MuonVtx_MuonNoVtx_pt;
      TH1F* h_ZeroBias_MuonVtx_MuonNoVtx_eta;
      TH1F* h_ZeroBias_MuonVtx_MuonNoVtx_phi;
      TH1F* h_ZeroBias_SVVtx_SVNoVtx_mass;


      TFile *file_out;

};

// Constructor
analyzer::analyzer(const edm::ParameterSet& iConfig) :
   triggerCache_(triggerExpression::Data(iConfig.getParameterSet("triggerConfiguration"), consumesCollector())),
   vtriggerAlias_(iConfig.getParameter<vector<string>>("triggerAlias")),
   vtriggerSelection_(iConfig.getParameter<vector<string>>("triggerSelection")),
   l1GtUtils_(nullptr)
{

   usesResource("TFileService");

   parameters = iConfig;

   vtriggerSelector_.reserve(vtriggerSelection_.size());
   vtriggerSelector_.push_back(triggerExpression::parse(vtriggerSelection_.at(0)));
   vtriggerSelector_.push_back(triggerExpression::parse(vtriggerSelection_.at(1)));
   vtriggerSelector_.push_back(triggerExpression::parse(vtriggerSelection_.at(2)));

   algToken_ = consumes<BXVector<GlobalAlgBlk>>(iConfig.getParameter<edm::InputTag>("AlgInputTag"));
   l1GtUtils_ = std::make_shared<l1t::L1TGlobalUtil>(iConfig, consumesCollector(), l1t::UseEventSetupIn::RunAndEvent);
   DoubleMu_l1Seeds_ = iConfig.getParameter<std::vector<std::string> >("DoubleMu_l1Seeds");
   for (unsigned int i = 0; i < DoubleMu_l1Seeds_.size(); i++){
     const auto& l1seed(DoubleMu_l1Seeds_.at(i));
     DoubleMu_l1Names[i] = TString(l1seed);
   }
   SingleMu_l1Seeds_ = iConfig.getParameter<std::vector<std::string> >("SingleMu_l1Seeds");
   for (unsigned int i = 0; i < SingleMu_l1Seeds_.size(); i++){
     const auto& l1seed(SingleMu_l1Seeds_.at(i));
     SingleMu_l1Names[i] = TString(l1seed);
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
analyzer::~analyzer() {
}


// beginJob (Before first event)
void analyzer::beginJob() {

   std::cout << "Begin Job" << std::endl;

   // Init the file and the TTree
   output_filename = parameters.getParameter<std::string>("nameOfOutput");
   file_out = new TFile(output_filename.c_str(), "RECREATE");

   // Analyzer parameters
   isData = parameters.getParameter<bool>("isData");
   is2024 = parameters.getParameter<bool>("is2024");

   // Binning
   std::vector<float> mbins; mbins.push_back(0.215);
   while (mbins.at(mbins.size()-1)<250)
     mbins.push_back(1.01*mbins.at(mbins.size()-1));

   // Histograms for DoubleMuon
   for (unsigned int i = 0; i < DoubleMu_l1Seeds_.size(); i++){
     h_DoubleMu_MuonNoVtx_pt.push_back(new TH1F(Form("h_DoubleMu_MuonNoVtx_pt_%s", DoubleMu_l1Names[i].Data()), "", 100, 0, 100));
     h_DoubleMu_MuonNoVtx_eta.push_back(new TH1F(Form("h_DoubleMu_MuonNoVtx_eta_%s", DoubleMu_l1Names[i].Data()), "", 100, -3, 3));
     h_DoubleMu_MuonNoVtx_phi.push_back(new TH1F(Form("h_DoubleMu_MuonNoVtx_phi_%s", DoubleMu_l1Names[i].Data()), "", 100, -3.14, 3.14));
     h_DoubleMu_SVNoVtx_mass.push_back(new TH1F(Form("h_DoubleMu_SVNoVtx_mass_%s", DoubleMu_l1Names[i].Data()), "", mbins.size()-1, mbins.data()));
   }
   h_DoubleMu_MuonNoVtx_pt.push_back(new TH1F("h_DoubleMu_MuonNoVtx_pt_Total", "", 100, 0, 100));
   h_DoubleMu_MuonNoVtx_eta.push_back(new TH1F("h_DoubleMu_MuonNoVtx_eta_Total", "", 100, -3, 3));
   h_DoubleMu_MuonNoVtx_phi.push_back(new TH1F("h_DoubleMu_MuonNoVtx_phi_Total", "", 100, -3.14, 3.14));
   h_DoubleMu_SVNoVtx_mass.push_back(new TH1F("h_DoubleMu_SVNoVtx_mass_Total", "", mbins.size()-1, mbins.data()));

   // Histograms for SingleMuon
   for (unsigned int i = 0; i < SingleMu_l1Seeds_.size(); i++){
     h_SingleMu_MuonVtx_pt.push_back(new TH1F(Form("h_SingleMu_MuonVtx_pt_%s", SingleMu_l1Names[i].Data()), "", 100, 0, 100));
     h_SingleMu_MuonVtx_eta.push_back(new TH1F(Form("h_SingleMu_MuonVtx_eta_%s", SingleMu_l1Names[i].Data()), "", 100, -3, 3));
     h_SingleMu_MuonVtx_phi.push_back(new TH1F(Form("h_SingleMu_MuonVtx_phi_%s", SingleMu_l1Names[i].Data()), "", 100, -3.14, 3.14));
   }
   h_SingleMu_MuonVtx_pt.push_back(new TH1F("h_SingleMu_MuonVtx_pt_Total", "", 100, 0, 100));
   h_SingleMu_MuonVtx_eta.push_back(new TH1F("h_SingleMu_MuonVtx_eta_Total", "", 100, -3, 3));
   h_SingleMu_MuonVtx_phi.push_back(new TH1F("h_SingleMu_MuonVtx_phi_Total", "", 100, -3.14, 3.14));

   // Histograms for ZeroBias
   h_ZeroBias_MuonVtx_pt = new TH1F("h_ZeroBias_MuonVtx_pt", "", 100, 0, 100);
   h_ZeroBias_MuonVtx_eta = new TH1F("h_ZeroBias_MuonVtx_eta", "", 100, -3, 3);
   h_ZeroBias_MuonVtx_phi = new TH1F("h_ZeroBias_MuonVtx_phi", "", 100, -3.14, 3.14);
   h_ZeroBias_MuonNoVtx_pt = new TH1F("h_ZeroBias_MuonNoVtx_pt", "", 100, 0, 100);
   h_ZeroBias_MuonNoVtx_eta = new TH1F("h_ZeroBias_MuonNoVtx_eta", "", 100, -3, 3);
   h_ZeroBias_MuonNoVtx_phi = new TH1F("h_ZeroBias_MuonNoVtx_phi", "", 100, -3.14, 3.14);

}

// endJob (After event loop has finished)
void analyzer::endJob()
{

    std::cout << "End Job" << std::endl;
    file_out->cd();
    counts->Write();
    for (unsigned int i = 0; i < DoubleMu_l1Seeds_.size() + 1; i++){
      h_DoubleMu_MuonNoVtx_pt.at(i)->Write();
      h_DoubleMu_MuonNoVtx_eta.at(i)->Write();
      h_DoubleMu_MuonNoVtx_phi.at(i)->Write();
      h_DoubleMu_SVNoVtx_mass.at(i)->Write();
    }
    for (unsigned int i = 0; i < SingleMu_l1Seeds_.size() + 1; i++){
      h_SingleMu_MuonVtx_pt.at(i)->Write();
      h_SingleMu_MuonVtx_eta.at(i)->Write();
      h_SingleMu_MuonVtx_phi.at(i)->Write();
    }
    h_ZeroBias_MuonNoVtx_pt->Write();
    h_ZeroBias_MuonNoVtx_eta->Write();
    h_ZeroBias_MuonNoVtx_phi->Write();
    h_ZeroBias_MuonVtx_pt->Write();
    h_ZeroBias_MuonVtx_eta->Write();
    h_ZeroBias_MuonVtx_phi->Write();
    file_out->Close();

}


// fillDescriptions
void analyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {

  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);

}

// Analyze (per event)
void analyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {

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
   if (verbose) std::cout << "Trigger analysis" << std::endl << std::endl;;
   bool DoubleMu_passHLT = false;
   bool SingleMu_passHLT = false;
   bool ZeroBias_passHLT = false;
   if (triggerCache_.setEvent(iEvent, iSetup)){
     if (vtriggerSelection_.at(0)!=""){
       auto& doublemu_vts(vtriggerSelector_.at(0));
       if (doublemu_vts){
         if (triggerCache_.configurationUpdated()) doublemu_vts->init(triggerCache_);
         DoubleMu_passHLT = (*doublemu_vts)(triggerCache_);
       }
     }
     if (vtriggerSelection_.at(1)!=""){
       auto& singlemu_vts(vtriggerSelector_.at(1));
       if (singlemu_vts && is2024){
         if (triggerCache_.configurationUpdated()) singlemu_vts->init(triggerCache_);
         SingleMu_passHLT = (*singlemu_vts)(triggerCache_);
       }
     }
     if (vtriggerSelection_.at(2)!=""){
       auto& zerobias_vts(vtriggerSelector_.at(2));
       if (zerobias_vts && is2024){
         if (triggerCache_.configurationUpdated()) zerobias_vts->init(triggerCache_);
         ZeroBias_passHLT = (*zerobias_vts)(triggerCache_);
       }
     }
   }
   if (!(DoubleMu_passHLT || SingleMu_passHLT || ZeroBias_passHLT))
       return;

   // -> L1 seeds
   l1GtUtils_->retrieveL1(iEvent, iSetup, algToken_);
   bool DoubleMu_passL1 = false;
   for (unsigned int i = 0; i < DoubleMu_l1Seeds_.size(); i++){
     const auto& l1seed(DoubleMu_l1Seeds_.at(i));
     bool l1htbit = 0;
     double prescale = -1;
     l1GtUtils_->getFinalDecisionByName(l1seed, l1htbit);
     l1GtUtils_->getPrescaleByName(l1seed, prescale);
     DoubleMu_l1Result[i] = l1htbit;
     DoubleMu_l1Prescale[i] = prescale;
     if (l1htbit) {
       DoubleMu_passL1 = true;
       if (verbose) std::cout << l1seed << " " << l1htbit << " " << prescale << std::endl;
     }
   }
   bool SingleMu_passL1 = false;
   if (is2024) {
     for (unsigned int i = 0; i < SingleMu_l1Seeds_.size(); i++){
       const auto& l1seed(SingleMu_l1Seeds_.at(i));
       bool l1htbit = 0;
       double prescale = -1;
       l1GtUtils_->getFinalDecisionByName(l1seed, l1htbit);
       l1GtUtils_->getPrescaleByName(l1seed, prescale);
       SingleMu_l1Result[i] = l1htbit;
       SingleMu_l1Prescale[i] = prescale;
       if (l1htbit) {
         SingleMu_passL1 = true;
         if (verbose) std::cout << l1seed << " " << l1htbit << " " << prescale << std::endl;
       }
     }
   }

   // SV association (NoVtx)
   std::vector<int> iSVNoVtx;
   std::vector<int> iSVNoVtxSel;
   std::vector<int> iMuAssocNoVtx;
   for (size_t i = 0; i < svsNoVtx->size(); i++) {
     const Run3ScoutingVertex& sv(svsNoVtx->at(i));
     if (!sv.isValidVtx())
       continue;
     iSVNoVtx.push_back(i);
   }
   //
   std::sort( std::begin(iSVNoVtx), std::end(iSVNoVtx), [&](int i1, int i2){ return ( (svsNoVtx->at(i1).chi2()/svsNoVtx->at(i1).ndof()) < (svsNoVtx->at(i2).chi2()/svsNoVtx->at(i2).ndof()) ); });
   //
   for (size_t i = 0; i < iSVNoVtx.size(); i++) {
     std::vector<int> MuAssocNoVtx_tmp;
     for (unsigned int j = 0; j < muonsNoVtx->size(); j++) {
        if(std::find(iMuAssocNoVtx.begin(), iMuAssocNoVtx.end(), j) != iMuAssocNoVtx.end())
          continue; 
        const Run3ScoutingMuon& muon(muonsNoVtx->at(j));
        for (auto idx:muon.vtxIndx()) {
          if (idx==int(iSVNoVtx.at(i))) {
            MuAssocNoVtx_tmp.push_back(j);
            break;
          }
        }
     }
     if (MuAssocNoVtx_tmp.size() == 2 && (muonsNoVtx->at(MuAssocNoVtx_tmp.at(0)).charge()*muonsNoVtx->at(MuAssocNoVtx_tmp.at(1)).charge() < 0) ){
       iMuAssocNoVtx.push_back(MuAssocNoVtx_tmp.at(0));
       iMuAssocNoVtx.push_back(MuAssocNoVtx_tmp.at(1));
       iSVNoVtxSel.push_back(i);
     } 
   }

   // DoubleMuon analysis
   if (verbose) std::cout << "DoubleMuon analysis" << std::endl;
   if (DoubleMu_passL1 && DoubleMu_passHLT)
   {
     // Loop over NoVtx muons: 
     int nMuonNoVtx_DoubleMu = 0;
     for (unsigned int i = 0; i < muonsNoVtx->size(); i++) {
       const Run3ScoutingMuon& muon(muonsNoVtx->at(i));
       // Per seed histograms
       for (unsigned int j = 0; j < DoubleMu_l1Seeds_.size(); j++) {
         if (DoubleMu_l1Result[j]) {
           h_DoubleMu_MuonNoVtx_pt.at(j)->Fill(muon.pt());
           h_DoubleMu_MuonNoVtx_eta.at(j)->Fill(muon.eta());
           h_DoubleMu_MuonNoVtx_phi.at(j)->Fill(muon.phi());
         }
       }
       // OR seed histograms
       h_DoubleMu_MuonNoVtx_pt.at(DoubleMu_l1Seeds_.size())->Fill(muon.pt());
       h_DoubleMu_MuonNoVtx_eta.at(DoubleMu_l1Seeds_.size())->Fill(muon.eta());
       h_DoubleMu_MuonNoVtx_phi.at(DoubleMu_l1Seeds_.size())->Fill(muon.phi());
       nMuonNoVtx_DoubleMu++; 
     }
     // Loop over NoVtx SVs
     for (unsigned int i = 0; i < iSVNoVtxSel.size(); i++) {
       const Run3ScoutingMuon& muon1(muonsNoVtx->at(iMuAssocNoVtx.at(i*2)));
       const Run3ScoutingMuon& muon2(muonsNoVtx->at(iMuAssocNoVtx.at(i*2+1)));
       TLorentzVector mu1; mu1.SetPtEtaPhiM(muon1.pt(), muon1.eta(), muon1.phi(), MUON_MASS);
       TLorentzVector mu2; mu2.SetPtEtaPhiM(muon2.pt(), muon2.eta(), muon2.phi(), MUON_MASS);
       float dimuon_mass = (mu1 + mu2).M();
       if (verbose)
         std::cout << "Detecter mass: " << dimuon_mass << std::endl;
       for (unsigned int j = 0; j < DoubleMu_l1Seeds_.size(); j++) {
         if (DoubleMu_l1Result[j])
           h_DoubleMu_SVNoVtx_mass.at(j)->Fill(dimuon_mass);
       }
       // OR seed histograms
       h_DoubleMu_SVNoVtx_mass.at(DoubleMu_l1Seeds_.size())->Fill(dimuon_mass);
     }
   }

   // SingleMuon analysis
   if (verbose) std::cout << "SingleMuon analysis" << std::endl;
   if (SingleMu_passL1 && SingleMu_passHLT && is2024)
   {
     // Loop over NoVtx muons: 
     int nMuonVtx_SingleMu = 0;
     for (unsigned int i = 0; i < muonsVtx->size(); i++) {
       const Run3ScoutingMuon& muon(muonsVtx->at(i));
       // Per seed histograms
       for (unsigned int j = 0; j < SingleMu_l1Seeds_.size(); j++) {
         if (SingleMu_l1Result[j]) {
           h_SingleMu_MuonVtx_pt.at(j)->Fill(muon.pt());
           h_SingleMu_MuonVtx_eta.at(j)->Fill(muon.eta());
           h_SingleMu_MuonVtx_phi.at(j)->Fill(muon.phi());
         }
       }
       // OR seed histograms
       h_SingleMu_MuonVtx_pt.at(SingleMu_l1Seeds_.size())->Fill(muon.pt());
       h_SingleMu_MuonVtx_eta.at(SingleMu_l1Seeds_.size())->Fill(muon.eta());
       h_SingleMu_MuonVtx_phi.at(SingleMu_l1Seeds_.size())->Fill(muon.phi());
       nMuonVtx_SingleMu++; 
     }
   }

   // ZeroBias analysis
   if (verbose) std::cout << "ZeroBias analysis" << std::endl;
   if (ZeroBias_passHLT && is2024)
   {
     // Loop over NoVtx muons: 
     int nMuonNoVtx_ZeroBias = 0;
     for (unsigned int i = 0; i < muonsNoVtx->size(); i++) {
       const Run3ScoutingMuon& muon(muonsNoVtx->at(i));
       h_ZeroBias_MuonNoVtx_pt->Fill(muon.pt());
       h_ZeroBias_MuonNoVtx_eta->Fill(muon.eta());
       h_ZeroBias_MuonNoVtx_phi->Fill(muon.phi());
       nMuonNoVtx_ZeroBias++; 
     }
     // Loop over Vtx muons: 
     int nMuonVtx_ZeroBias = 0;
     for (unsigned int i = 0; i < muonsVtx->size(); i++) {
       const Run3ScoutingMuon& muon(muonsVtx->at(i));
       h_ZeroBias_MuonVtx_pt->Fill(muon.pt());
       h_ZeroBias_MuonVtx_eta->Fill(muon.eta());
       h_ZeroBias_MuonVtx_phi->Fill(muon.phi());
       nMuonVtx_ZeroBias++; 
     }
   }

}

DEFINE_FWK_MODULE(analyzer);
