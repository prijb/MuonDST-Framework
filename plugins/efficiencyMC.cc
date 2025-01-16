#include <memory>
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

#include "DataFormats/Math/interface/deltaR.h"

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

#include "TLorentzVector.h"
#include "TTree.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TFile.h"
#include "TEfficiency.h"


class efficiencyMC : public edm::one::EDAnalyzer<edm::one::SharedResources>  {
   public:
      explicit efficiencyMC(const edm::ParameterSet&);
      ~efficiencyMC();

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

      // "hltScoutingMuonPackerNoVtx" (Updated)
      edm::EDGetTokenT<edm::View<Run3ScoutingMuon> > muonsNoVtxToken;
      edm::Handle<edm::View<Run3ScoutingMuon> > muonsNoVtx;
      // "hltScoutingMuonPackerVtx" (Updated)
      edm::EDGetTokenT<edm::View<Run3ScoutingMuon> > muonsVtxToken;
      edm::Handle<edm::View<Run3ScoutingMuon> > muonsVtx;
      // "hltScoutingMuonPacker" (Old)
      edm::EDGetTokenT<edm::View<Run3ScoutingMuon> > muonsToken;
      edm::Handle<edm::View<Run3ScoutingMuon> > muons;
      // GenParticles
      edm::EDGetTokenT<edm::View<reco::GenParticle> > genToken;
      edm::Handle<edm::View<reco::GenParticle> > gens;

      //
      // --- Variables
      //

      bool isData = false;

      // --- HLT
      edm::EDGetTokenT<edm::TriggerResults> triggerBits_;
      triggerExpression::Data triggerCache_;

      //
      // --- Output
      //
      std::string output_filename;

      TH1F* histo_pt_gen;
      TH1F* histo_eta_gen;
      TH1F* histo_phi_gen;
      TH1F* histo_lxy_gen;
      TH1F* histo_pt_gen_isNoVtx;
      TH1F* histo_eta_gen_isNoVtx;
      TH1F* histo_phi_gen_isNoVtx;
      TH1F* histo_lxy_gen_isNoVtx;
      TH1F* histo_pt_gen_isVtx;
      TH1F* histo_eta_gen_isVtx;
      TH1F* histo_phi_gen_isVtx;
      TH1F* histo_lxy_gen_isVtx;

      TH2F* histo_pt_comp_isNoVtx;
      TH2F* histo_pt_comp_isVtx;

      TH1F* histo_pt_std;
      TH1F* histo_eta_std;
      TH1F* histo_phi_std;

      TH1F* histo_pt_vtx;
      TH1F* histo_eta_vtx;
      TH1F* histo_phi_vtx;

      TH1F* histo_pt_novtx;
      TH1F* histo_eta_novtx;
      TH1F* histo_phi_novtx;

      TEfficiency *efficiency_pt_std;
      TEfficiency *efficiency_pt_vtx;
      TEfficiency *efficiency_pt_novtx;
      TEfficiency *efficiency_pt_or;
      TEfficiency *efficiency_lxy_vtx;
      TEfficiency *efficiency_lxy_novtx;
      TEfficiency *efficiency_lxy_or;

      TEfficiency *efficiency_trg_DoubleMuonVtx;
      TEfficiency *efficiency_trg_DoubleMuonNoVtx;
      TEfficiency *efficiency_trg_DoubleMuonOR;

      TH1F *counts;
      TFile *file_out;

};

// Constructor
efficiencyMC::efficiencyMC(const edm::ParameterSet& iConfig) :
   triggerCache_(triggerExpression::Data(iConfig.getParameterSet("triggerConfiguration"),
   
   consumesCollector()))
{

   usesResource("TFileService");

   parameters = iConfig;

   counts = new TH1F("counts", "", 1, 0, 1);

   histo_pt_gen = new TH1F("histo_pt_gen", ";Generated muon p_{T} (GeV); Number of muons", 100, 0, 50);
   histo_eta_gen = new TH1F("histo_eta_gen", ";Generated muon #eta; Number of muons", 30, -4, 4);
   histo_phi_gen = new TH1F("histo_phi_gen", ";Generated muon #phi (rad); Number of muons", 30, -3.2, 3.2);
   histo_lxy_gen = new TH1F("histo_lxy_gen", ";Generated muon l_{xy} (cm); Number of muons", 30, 0.0, 30.0);
   histo_pt_gen_isNoVtx = new TH1F("histo_pt_gen_isNoVtx", ";Generated muon p_{T} (GeV); Number of muons", 100, 0, 50);
   histo_eta_gen_isNoVtx = new TH1F("histo_eta_gen_isNoVtx", ";Generated muon #eta; Number of muons", 30, -4, 4);
   histo_phi_gen_isNoVtx = new TH1F("histo_phi_gen_isNoVtx", ";Generated muon #phi (rad); Number of muons", 30, -3.2, 3.2);
   histo_lxy_gen_isNoVtx = new TH1F("histo_lxy_gen_isNoVtx", ";Generated muon l_{xy} (cm); Number of muons", 30, 0.0, 30.0);
   histo_pt_gen_isVtx = new TH1F("histo_pt_gen_isVtx", ";Generated muon p_{T} (GeV); Number of muons", 100, 0, 50);
   histo_eta_gen_isVtx = new TH1F("histo_eta_gen_isVtx", ";Generated muon #eta; Number of muons", 30, -4, 4);
   histo_phi_gen_isVtx = new TH1F("histo_phi_gen_isVtx", ";Generated muon #phi (rad); Number of muons", 30, -3.2, 3.2);
   histo_lxy_gen_isVtx = new TH1F("histo_lxy_gen_isVtx", ";Generated muon l_{xy} (cm); Number of muons", 30, 0.0, 30.0);

   histo_pt_comp_isNoVtx = new TH2F("histo_pt_comp_isNoVtx", ";Generated muon p_{T} (GeV); Reconstructed muon p_{T} (GeV)", 100, 0, 100, 100, 0, 100);
   histo_pt_comp_isVtx   = new TH2F("histo_pt_comp_isVtx", ";Generated muon p_{T} (GeV); Reconstructed muon p_{T} (GeV)", 100, 0, 100, 100, 0, 100);

   histo_pt_std = new TH1F("histo_pt_std", ";Scouting muon p_{T} (GeV); Number of muons", 100, 0, 50);
   histo_eta_std = new TH1F("histo_eta_std", ";Scouting muon #eta; Number of muons", 30, -4, 4);
   histo_phi_std = new TH1F("histo_phi_std", ";Scouting muon #phi (rad); Number of muons", 30, -3.2, 3.2);

   histo_pt_vtx = new TH1F("histo_pt_vtx", ";Scouting muon p_{T} (GeV); Number of muons", 100, 0, 50);
   histo_eta_vtx = new TH1F("histo_eta_vtx", ";Scouting muon #eta; Number of muons", 30, -4, 4);
   histo_phi_vtx = new TH1F("histo_phi_vtx", ";Scouting muon #phi (rad); Number of muons", 30, -3.2, 3.2);

   histo_pt_novtx = new TH1F("histo_pt_novtx", ";Scouting muon p_{T} (GeV); Number of muons", 100, 0, 50);
   histo_eta_novtx = new TH1F("histo_eta_novtx", ";Scouting muon #eta; Number of muons", 30, -4, 4);
   histo_phi_novtx = new TH1F("histo_phi_novtx", ";Scouting muon #phi (rad); Number of muons", 30, -3.2, 3.2);

   efficiency_pt_std = new TEfficiency("efficiency_pt_std", ";Generated p_{T} (GeV); HLT efficiency", 100, 0, 50);
   efficiency_pt_vtx = new TEfficiency("efficiency_pt_vtx", ";Generated p_{T} (GeV); HLT efficiency", 100, 0, 50);
   efficiency_pt_novtx = new TEfficiency("efficiency_pt_novtx", ";Generated p_{T} (GeV); HLT efficiency", 100, 0, 50);
   efficiency_pt_or = new TEfficiency("efficiency_pt_or", ";Generated p_{T} (GeV); HLT efficiency", 100, 0, 50);
   efficiency_lxy_vtx = new TEfficiency("efficiency_lxy_vtx", ";Generated l_{xy} (cm); HLT efficiency", 40, 0, 80);
   efficiency_lxy_novtx = new TEfficiency("efficiency_lxty_novtx", ";Generated l_{xy} (cm); HLT efficiency", 40, 0, 80);
   efficiency_lxy_or = new TEfficiency("efficiency_lxty_or", ";Generated l_{xy} (cm); HLT efficiency", 40, 0, 80);

   efficiency_trg_DoubleMuonVtx = new TEfficiency("efficiency_trg_DoubleMuonVtx", "DoubleMuonVtx efficiency; Leading p_{T} (GeV) ; Subleading p_{T} (GeV)", 20, 0, 40, 20, 0, 40);
   efficiency_trg_DoubleMuonNoVtx = new TEfficiency("efficiency_trg_DoubleMuonNoVtx", "DoubleMuonNoVtx efficiency; Leading p_{T} (GeV) ; Subleading p_{T} (GeV)", 20, 0, 40, 20, 0, 40);
   efficiency_trg_DoubleMuonOR = new TEfficiency("efficiency_trg_DoubleMuonOR", "DoubleMuonOR efficiency; Leading p_{T} (GeV) ; Subleading p_{T} (GeV)", 20, 0, 40, 20, 0 , 40);

   isData = parameters.getParameter<bool>("isData");
   muonsVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerVtx"));
   muonsNoVtxToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPackerNoVtx"));
   muonsToken = consumes<edm::View<Run3ScoutingMuon> >  (parameters.getParameter<edm::InputTag>("muonPacker"));
   genToken = consumes<edm::View<reco::GenParticle> >  (parameters.getParameter<edm::InputTag>("generatedParticles"));

}


// Destructor
efficiencyMC::~efficiencyMC() {
}


// beginJob (Before first event)
void efficiencyMC::beginJob() {

   std::cout << "Begin Job" << std::endl;

   // Init the file and the TTree
   output_filename = parameters.getParameter<std::string>("nameOfOutput");
   file_out = new TFile(output_filename.c_str(), "RECREATE");

   // Analyzer parameters
   isData = parameters.getParameter<bool>("isData");


}

// endJob (After event loop has finished)
void efficiencyMC::endJob()
{

    std::cout << "End Job" << std::endl;
    file_out->cd();
    counts->Write();

    histo_pt_gen->Write();
    histo_eta_gen->Write();
    histo_phi_gen->Write();
    histo_lxy_gen->Write();
    histo_pt_gen_isNoVtx->Write();
    histo_eta_gen_isNoVtx->Write();
    histo_phi_gen_isNoVtx->Write();
    histo_lxy_gen_isNoVtx->Write();
    histo_pt_gen_isVtx->Write();
    histo_eta_gen_isVtx->Write();
    histo_phi_gen_isVtx->Write();
    histo_lxy_gen_isVtx->Write();

    std::cout << histo_pt_comp_isNoVtx->GetName() << std::endl;
    histo_pt_comp_isNoVtx->Write();
    std::cout << histo_pt_comp_isVtx->GetName() << std::endl;
    histo_pt_comp_isVtx->Write();

    histo_pt_std->Write();
    histo_eta_std->Write();
    histo_phi_std->Write();

    histo_pt_vtx->Write();
    histo_eta_vtx->Write();
    histo_phi_vtx->Write();

    histo_pt_novtx->Write();
    histo_eta_novtx->Write();
    histo_phi_novtx->Write();

    efficiency_pt_std->Write();
    efficiency_pt_vtx->Write();
    efficiency_pt_novtx->Write();
    efficiency_pt_or->Write();
    efficiency_lxy_vtx->Write();
    efficiency_lxy_novtx->Write();
    efficiency_lxy_or->Write();

    efficiency_trg_DoubleMuonVtx->Write();
    efficiency_trg_DoubleMuonNoVtx->Write();
    efficiency_trg_DoubleMuonOR->Write();

    file_out->Close();

}


// fillDescriptions
void efficiencyMC::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {

  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);

}

// Analyze (per event)
void efficiencyMC::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {

   bool validNoVtx = iEvent.getByToken(muonsNoVtxToken, muonsNoVtx);
   bool validVtx = iEvent.getByToken(muonsVtxToken, muonsVtx);
   bool validStd = iEvent.getByToken(muonsToken, muons);
   iEvent.getByToken(genToken, gens);

   // Fill histograms
   if (validStd) {
     for (const auto& mu : *muons){
       histo_pt_std->Fill(mu.pt());
       histo_eta_std->Fill(mu.eta());
       histo_phi_std->Fill(mu.phi());
     }
   }
   if (validVtx) {
     for (const auto& mu : *muonsVtx){
       histo_pt_vtx->Fill(mu.pt());
       histo_eta_vtx->Fill(mu.eta());
       histo_phi_vtx->Fill(mu.phi());
     }
   }
   if (validNoVtx) {
     for (const auto& mu : *muonsNoVtx){
       histo_pt_novtx->Fill(mu.pt());
       histo_eta_novtx->Fill(mu.eta());
       histo_phi_novtx->Fill(mu.phi());
     }
   }

    // Fill efficiencies (wrt generation)
    std::vector<float> muon_pt;
    for (const auto& gp : *gens) {

        if (fabs(gp.pdgId()) != 13)
          continue;

        if (gp.status() != 1)
          continue;

        // Get Pt
        muon_pt.push_back(gp.pt());

        // Get lxy distance
        reco::GenParticleRef mref;
        reco::GenParticle m;
        if (gp.mother()->pdgId() == gp.pdgId()) {
          mref = gp.motherRef();
          m = *mref;
          while (m.pdgId() == m.mother()->pdgId()) {
            mref = m.motherRef();
            m = *mref;
          }
        } else {
          m = gp;
        }

        //std::cout << fabs(m.mother()->pdgId()) << std::endl;
        if (fabs(m.mother()->pdgId()) != 1023 && fabs(m.mother()->pdgId()) != 6000211)
          continue;

        double vx = m.vx();
        double vy = m.vy();
        double vz = m.vz();
        double lxy = sqrt(vx*vx + vy*vy);

        histo_pt_gen->Fill(gp.pt());
        histo_eta_gen->Fill(gp.eta());
        histo_phi_gen->Fill(gp.phi());
        histo_lxy_gen->Fill(lxy);

        //
        // Match with scouting muons (NoVtx standard 2022 and 2023)
        float delR_std = 999.;
        Run3ScoutingMuon best_std;
        if (validStd) {
          for (const auto& mu : *muons){
            float _delPhi = deltaPhi(gp.phi(), mu.phi());
            float _delR = sqrt(_delPhi*_delPhi + (mu.eta() - gp.eta())*(mu.eta() - gp.eta()));
            if (_delR < delR_std) {
              best_std = mu;
              delR_std = _delR;
            }
          }
          // Fill efficiency
          if (delR_std < 0.2) {
            efficiency_pt_std->Fill(true, gp.pt());
          } else {
            efficiency_pt_std->Fill(false, gp.pt());
          }
        }

        //
        // Match with scouting muons (NoVtx)
        float delR_novtx = 999.;
        Run3ScoutingMuon best_novtx;
        unsigned int best_idx_novtx = 999;
        std::vector<unsigned int> matched_novtx;
        if (validNoVtx) {
            //for (const auto& mu : *muonsNoVtx){
            for (unsigned int i = 0; i < muonsNoVtx->size(); i++){
                if (std::find(matched_novtx.begin(), matched_novtx.end(), i) != matched_novtx.end())
                    continue;
                const auto& mu = muonsNoVtx->at(i);
                float _delPhi = deltaPhi(gp.phi(), mu.phi());
                float _delR = sqrt(_delPhi*_delPhi + (mu.eta() - gp.eta())*(mu.eta() - gp.eta()));
                float _delPt = fabs(1./gp.pt() - 1./mu.pt());
                if (_delR < delR_novtx) {
                    best_idx_novtx = i;
                    best_novtx = mu;
                    delR_novtx = _delR;
                }
            }
            // Fill efficiency
            if (delR_novtx < 0.1) {
                matched_novtx.push_back(best_idx_novtx);
                histo_pt_gen_isNoVtx->Fill(gp.pt());
                histo_lxy_gen_isNoVtx->Fill(lxy);
                histo_pt_comp_isNoVtx->Fill(gp.pt(), best_novtx.pt());
                efficiency_pt_novtx->Fill(true, gp.pt());
                efficiency_lxy_novtx->Fill(true, lxy);
            } else {
                efficiency_pt_novtx->Fill(false, gp.pt());
                efficiency_lxy_novtx->Fill(false, lxy);
            }
        }

        //
        // Match with scouting muons (Vtx)
        float delR_vtx = 999.;
        Run3ScoutingMuon best_vtx;
        unsigned int best_idx_vtx = 999;
        std::vector<unsigned int> matched_vtx;
        if (validNoVtx) {
            //for (const auto& mu : *muonsVtx){
            for (unsigned int i = 0; i < muonsVtx->size(); i++){
                if (std::find(matched_vtx.begin(), matched_vtx.end(), i) != matched_vtx.end())
                    continue;
                const auto& mu = muonsVtx->at(i);
                float _delPhi = deltaPhi(gp.phi(), mu.phi());
                float _delR = sqrt(_delPhi*_delPhi + (mu.eta() - gp.eta())*(mu.eta() - gp.eta()));
                float _delPt = fabs(1./gp.pt() - 1./mu.pt());
                if (_delR < delR_vtx) {
                    best_idx_vtx = i;
                    best_vtx = mu;
                    delR_vtx = _delR;
                }
            }
            // Fill efficiency
            if (delR_vtx < 0.1) {
                matched_vtx.push_back(best_idx_vtx);
                histo_pt_gen_isVtx->Fill(gp.pt());
                histo_lxy_gen_isVtx->Fill(lxy);
                histo_pt_comp_isVtx->Fill(gp.pt(), best_vtx.pt());
                efficiency_pt_vtx->Fill(true, gp.pt());
                efficiency_lxy_vtx->Fill(true, lxy);
            } else {
                efficiency_pt_vtx->Fill(false, gp.pt());
                efficiency_lxy_vtx->Fill(false, lxy);
            }
        }

        if (validNoVtx && (validVtx)) {
          if (delR_vtx < 0.1 || delR_novtx < 0.1) {
             efficiency_pt_or->Fill(true, gp.pt());
             efficiency_lxy_or->Fill(true, lxy);
          } else {
             efficiency_pt_or->Fill(false, gp.pt());
             efficiency_lxy_or->Fill(false, lxy);
          }
        }

    }

    // Trigger evaluation
    bool passNoVtxHLT = false;
    bool passVtxHLT = false;
    std::cout << muon_pt.size() << std::endl;
    if (muon_pt.size() > 1) {
        std::sort( std::begin(muon_pt), std::end(muon_pt), [&](int i1, int i2){ return i1 > i2; });
        /*
        const edm::TriggerNames &names = iEvent.triggerNames(*triggerBits);
        for (unsigned int itrg = 0; itrg < triggerBits->size(); ++itrg) {
         TString TrigPath = names.triggerName(itrg);
         if (TrigPath.Contains("DST_PFScouting_DoubleMuon_v")){
           if (triggerBits->accept(itrg)) {
             passNoVtxHLT = true;
             continue;
           }
           break
         }
         std::cout << path << "\t" << TrigPath << std::endl;
        }
        */
        
        if (triggerCache_.setEvent(iEvent, iSetup)){
          const auto& vts_dimu_novtx(triggerExpression::parse("DST_PFScouting_ZeroBias_v*"));
          if (vts_dimu_novtx){
             std::cout << "Hola" << std::endl;
             if (triggerCache_.configurationUpdated()) vts_dimu_novtx->init(triggerCache_);
             passNoVtxHLT = (*vts_dimu_novtx)(triggerCache_);
             std::cout << passNoVtxHLT << "" << muon_pt.at(0) <<  "" << muon_pt.at(1) << std::endl;
          }
          //const auto& vts_dimu_vtx(triggerExpression::parse("DST_PFScouting_DoubleMuonVtx_v6"));
          //if (vts_dimu_vtx){
          //   if (triggerCache_.configurationUpdated()) vts_dimu_vtx->init(triggerCache_);
          //   passVtxHLT = (*vts_dimu_vtx)(triggerCache_);
          //}
        } 
        
        efficiency_trg_DoubleMuonVtx->Fill(passVtxHLT, muon_pt.at(1), muon_pt.at(0));
        efficiency_trg_DoubleMuonNoVtx->Fill(passNoVtxHLT, muon_pt.at(1), muon_pt.at(0));
        efficiency_trg_DoubleMuonOR->Fill((passVtxHLT || passNoVtxHLT), muon_pt.at(1), muon_pt.at(0));
    }
    
    

    // Count number of events read
    counts->Fill(0);

}

DEFINE_FWK_MODULE(efficiencyMC);
