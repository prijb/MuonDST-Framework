#include <memory>
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/EDProducer.h"
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

#include <string>
#include <iostream>
#include <vector>
#include <algorithm>

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

      // displacedGlobalMuons (reco::Track)
      edm::EDGetTokenT<edm::View<reco::Track> > dglToken;
      edm::Handle<edm::View<reco::Track> > dgls;
      // displacedStandAloneMuons (reco::Track)
      edm::EDGetTokenT<edm::View<reco::Track> > dsaToken;
      edm::Handle<edm::View<reco::Track> > dsas;
      // displacedMuons (reco::Muon // pat::Muon)
      edm::EDGetTokenT<edm::View<pat::Muon> > dmuToken;
      edm::Handle<edm::View<pat::Muon> > dmuons;

      //
      // --- Variables
      //

      bool isData = false;

      // Event
      Int_t event = 0;
      Int_t lumiBlock = 0;
      Int_t run = 0;

      // displacedGlobalMuons
      Int_t ndgl = 0;
      Float_t dgl_pt[200] = {0.};
      Float_t dgl_eta[200] = {0.};
      Float_t dgl_phi[200] = {0.};
      Int_t dgl_nhits[200] = {0};

      // displacedStandAloneMuons
      Int_t ndsa = 0;
      Float_t dsa_pt[200] = {0.};
      Float_t dsa_eta[200] = {0.};
      Float_t dsa_phi[200] = {0.};
      Int_t dsa_nhits[200] = {0};

      // displacedMuons
      Int_t ndmu = 0;
      Float_t dmu_pt[200] = {0.};
      Float_t dmu_eta[200] = {0.};
      Float_t dmu_phi[200] = {0.};
      Int_t dmu_isDSA[200] = {0};
      Int_t dmu_isDGL[200] = {0};
      Int_t dmu_isDTK[200] = {0};
      Float_t dmu_dsa_pt[200] = {0.};

      //
      // --- Output
      //
      std::string output_filename;
      TH1F *counts;
      TFile *file_out;
      TTree *tree_out;

};

// Constructor
ntuplizer::ntuplizer(const edm::ParameterSet& iConfig) {

   usesResource("TFileService");

   parameters = iConfig;

   counts = new TH1F("counts", "", 1, 0, 1);

   isData = consumes<edm::View<reco::Track> >  (parameters.getParameter<edm::InputTag>("displacedGlobalCollection"));
   dglToken = consumes<edm::View<reco::Track> >  (parameters.getParameter<edm::InputTag>("displacedGlobalCollection"));
   dsaToken = consumes<edm::View<reco::Track> >  (parameters.getParameter<edm::InputTag>("displacedStandAloneCollection"));
   dmuToken = consumes<edm::View<pat::Muon> >  (parameters.getParameter<edm::InputTag>("displacedMuonCollection"));

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

   tree_out->Branch("ndgl", &ndgl, "ndgl/I");
   tree_out->Branch("dgl_pt", dgl_pt, "dgl_pti[ndgl]/F");
   tree_out->Branch("dgl_eta", dgl_eta, "dgl_eta[ndgl]/F");
   tree_out->Branch("dgl_phi", dgl_phi, "dgl_phi[ndgl]/F");
   tree_out->Branch("dgl_nhits", dgl_nhits, "dgl_nhits[ndgl]/I");

   tree_out->Branch("ndsa", &ndsa, "ndsa/I");
   tree_out->Branch("dsa_pt", dsa_pt, "dsa_pt[ndsa]/F");
   tree_out->Branch("dsa_eta", dsa_eta, "dsa_eta[ndsa]/F");
   tree_out->Branch("dsa_phi", dsa_phi, "dsa_phi[ndsa]/F");
   tree_out->Branch("dsa_nhits", dsa_nhits, "dsa_nhits[ndsa]/I");

   tree_out->Branch("ndmu", &ndmu, "ndmu/I");
   tree_out->Branch("dmu_pt", dmu_pt, "dmu_pt[ndmu]/F");
   tree_out->Branch("dmu_eta", dmu_eta, "dmu_eta[ndmu]/F");
   tree_out->Branch("dmu_phi", dmu_phi, "dmu_phi[ndmu]/F");
   tree_out->Branch("dmu_isDSA", dmu_isDSA, "dmu_isDSA[ndmu]/I");
   tree_out->Branch("dmu_isDGL", dmu_isDGL, "dmu_isDGL[ndmu]/I");
   tree_out->Branch("dmu_isDTK", dmu_isDTK, "dmu_isDTK[ndmu]/I");
   tree_out->Branch("dmu_dsa_pt", dmu_dsa_pt, "dmu_dsa_pt[ndmu]/F");


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

   iEvent.getByToken(dglToken, dgls);
   iEvent.getByToken(dsaToken, dsas);
   iEvent.getByToken(dmuToken, dmuons);

   // Count number of events read
   counts->Fill(0);


   // -> Event info
   event = iEvent.id().event();
   lumiBlock = iEvent.id().luminosityBlock();
   run = iEvent.id().run();


   // displacedGlobalMuons
   ndgl = 0;
   for (unsigned int i = 0; i < dgls->size(); i++) {
     const reco::Track& dgl(dgls->at(i));
     dgl_pt[ndgl] = dgl.pt();
     dgl_eta[ndgl] = dgl.eta();
     dgl_phi[ndgl] = dgl.phi();
     dgl_nhits[ndgl] = dgl.hitPattern().numberOfValidHits();
     ndgl++;
   }

   // displacedStandAloneMuons
   ndsa = 0;
   for (unsigned int i = 0; i < dsas->size(); i++) {
     const reco::Track& dsa(dsas->at(i));
     dsa_pt[ndsa] = dsa.pt();
     dsa_eta[ndsa] = dsa.eta();
     dsa_phi[ndsa] = dsa.phi();
     dsa_nhits[ndsa] = dsa.hitPattern().numberOfValidHits();
     ndsa++;
   }

   // displacedMuons
   ndmu = 0;;
   for (unsigned int i = 0; i < dmuons->size(); i++) {
     const pat::Muon& dmuon(dmuons->at(i));
     dmu_pt[ndmu] = dmuon.pt();
     dmu_eta[ndmu] = dmuon.eta();
     dmu_phi[ndmu] = dmuon.phi();
     dmu_isDGL[ndmu] = dmuon.isGlobalMuon();
     dmu_isDSA[ndmu] = dmuon.isStandAloneMuon();
     dmu_isDTK[ndmu] = dmuon.isTrackerMuon();

     // Access the DSA track associated to the displacedMuon
     if ( dmuon.isStandAloneMuon() ) {
       const reco::Track* outerTrack = (dmuon.standAloneMuon()).get();
       dmu_dsa_pt[ndmu] = outerTrack->pt();
     }

     ndmu++;
   }


   // -> Fill tree
   tree_out->Fill();

}

DEFINE_FWK_MODULE(ntuplizer);
