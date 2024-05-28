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

#include <string>
#include <iostream>
#include <vector>
#include <algorithm>

#include "TLorentzVector.h"
#include "TTree.h"
#include "TH1F.h"
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

      //
      // --- Output
      //
      std::string output_filename;

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

      TH1F *counts;
      TFile *file_out;

};

// Constructor
efficiencyMC::efficiencyMC(const edm::ParameterSet& iConfig) {

   usesResource("TFileService");

   parameters = iConfig;

   counts = new TH1F("counts", "", 1, 0, 1);

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

   iEvent.getByToken(muonsNoVtxToken, muonsNoVtx);
   iEvent.getByToken(muonsVtxToken, muonsVtx);
   iEvent.getByToken(muonsToken, muons);
   iEvent.getByToken(genToken, gens);

   // Fill histograms
   for (const auto& mu : *muons){
     histo_pt_std->Fill(mu.pt());
     histo_eta_std->Fill(mu.eta());
     histo_phi_std->Fill(mu.phi());
   }
   for (const auto& mu : *muonsVtx){
     histo_pt_vtx->Fill(mu.pt());
     histo_eta_vtx->Fill(mu.eta());
     histo_phi_vtx->Fill(mu.phi());
   }
   for (const auto& mu : *muonsNoVtx){
     histo_pt_novtx->Fill(mu.pt());
     histo_eta_novtx->Fill(mu.eta());
     histo_phi_novtx->Fill(mu.phi());
   }

   // Fill efficiencies (wrt generation)
   for (const auto& gp : *gens) {

     if (fabs(gp.pdgId()) != 13)
       continue;

     if (gp.status() != 1)
       continue;

     //h_gen_pt->Fill(gp.pt());
     //h_gen_eta->Fill(gp.eta());
     //h_gen_phi->Fill(gp.phi());

     //
     // Match with scouting muons (NoVtx standard 2022 and 2023)
     float delR_std = 999.;
     Run3ScoutingMuon best_std;
     for (const auto& mu : *muons){
       float _delPhi = deltaPhi(gp.phi(), mu.phi());
       float _delR = sqrt(_delPhi*_delPhi + (mu.eta() - gp.eta())*(mu.eta() - gp.eta()));
       if (_delR < delR_std) {
         best_std = mu;
         delR_std = _delR;
       }
     }

     //
     // Match with scouting muons (NoVtx updated)
     float delR_novtx = 999.;
     Run3ScoutingMuon best_novtx;
     for (const auto& mu : *muonsNoVtx){
       float _delPhi = deltaPhi(gp.phi(), mu.phi());
       float _delR = sqrt(_delPhi*_delPhi + (mu.eta() - gp.eta())*(mu.eta() - gp.eta()));
       if (_delR < delR_novtx) {
         best_novtx = mu;
         delR_novtx = _delR;
       }
     }

     // Fill efficiencies
     if (delR_novtx < 0.2) {
       efficiency_pt_novtx->Fill(true, gp.pt());
     } else {
       efficiency_pt_novtx->Fill(false, gp.pt());
     }
     if (delR_std < 0.2) {
       efficiency_pt_std->Fill(true, gp.pt());
     } else {
       efficiency_pt_std->Fill(false, gp.pt());
     }


   }


   // Count number of events read
   counts->Fill(0);

}

DEFINE_FWK_MODULE(efficiencyMC);
