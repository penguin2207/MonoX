#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TLorentzVector.h"
#include "TROOT.h"
#include "TEntryListArray.h"
#include "TEfficiency.h"

#include "Objects/interface/EventMonophoton.h"

#include <cmath>

class Calculator {
public:
  enum Era {
    Spring15,
    Spring16,
    Ashim_ZG_CWIso,
    Ashim_GJets_CIso,
    nEras
  };

  enum WP {
    WPloose,
    WPmedium,
    WPtight
  };

  enum Cut {
    sMatch,
    sHoverE,
    sSieie,
    sNHIso,
    sPhIso,
    sCHIso,
    sEveto,
    sSpike,
    sHalo,
    sCHMaxIso,
    nCuts
  };

  static TString cutNames[nCuts];

  Calculator() {}
  unsigned calculate(TTree* _input, TFile* _outputFile);

  void setMinPhoPt(float minPhoPt) { minPhoPt_ = minPhoPt; }
  void setMaxPhoPt(float maxPhoPt) { maxPhoPt_ = maxPhoPt; }
  void setMinMet(float minMet) { minMet_ = minMet; }
  void setMaxMet(float maxMet) { maxMet_ = maxMet; }
  void setMinEta(float minEta) { minEta_ = minEta; }
  void setMaxEta(float maxEta) { maxEta_ = maxEta; }
  
  void setMaxDR(float maxDR) { maxDR_ = maxDR; }
  void setMaxDPt(float maxDPt) { maxDPt_ = maxDPt; }

  void setWorkingPoint(WP wp) { wp_ = wp; }
  void setEra(Era era) { era_ = era; }

private:
  double minPhoPt_{175.};
  double maxPhoPt_{6500.};
  double minMet_{0.};
  double maxMet_{60.};
  double minEta_{0.};
  double maxEta_{1.5};
  
  double maxDR_{0.2};
  double maxDPt_{0.2};

  WP wp_{WPmedium};
  Era era_{Spring16};
};

TString Calculator::cutNames[Calculator::nCuts] = {
  "Match",
  "HoverE",
  "Sieie",
  "NHIso",
  "PhIso",
  "CHIso",
  "Eveto",
  "Spike",
  "Halo",
  "CHMaxIso"
};

unsigned
Calculator::calculate(TTree* _input, TFile* _outputFile)
{
  panda::EventMonophoton event;
  event.setReadRunTree(false);

  _input->SetBranchStatus("*", false);
  event.setAddress(*_input, {"runNumber", "lumiNumber", "eventNumber", "weight", "npv", "npvTrue", "genParticles", "photons", "t1Met", "rho", "superClusters"});
  double minGenPt_ = minPhoPt_ / ( 1 + maxDPt_ );
  double maxGenPt_ = maxPhoPt_ / ( 1 - maxDPt_ );
  double minGenEta_ = std::max(0., minEta_ - maxDR_);
  double maxGenEta_ = maxEta_ + maxDR_;

  printf("%.0f < gen pt  < %.0f \n", minGenPt_, maxGenPt_);
  printf("%.2f < gen eta < %.2f \n", minGenEta_, maxGenEta_);

  _outputFile->cd();
  auto* output(new TTree("cutflow", "cutflow"));
  event.book(*output, {"runNumber", "lumiNumber", "eventNumber", "npv"});

  float pt;
  float eta;
  float phi;
  output->Branch("pt", &pt, "pt/F");
  output->Branch("eta", &eta, "eta/F");
  output->Branch("phi", &phi, "phi/F");

  bool results[nCuts]{};
  for (unsigned iC(0); iC != nCuts; ++iC)
    output->Branch(cutNames[iC], results + iC, cutNames[iC] + "/O");

  unsigned nGenPhotons(0);
  unsigned nMatchedPhotons(0);

  long iEntry(0);
  while (event.getEntry(*_input, iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << " " << iEntry << std::endl;
    
    if (event.t1Met.pt > maxMet_ || event.t1Met.pt < minMet_)
      continue;

    std::fill_n(results, nCuts, false);

    std::vector<panda::UnpackedGenParticle const*> genPhotons;

    for (auto& gen : event.genParticles) {
      // 22 is already testFlag-ed to be IsPrompt in EventMonophoton::copyGenParticles
      if (gen.pdgid != 22)
        continue;

      if ( gen.pt() < minGenPt_ || gen.pt() > maxGenPt_ )
        continue;

      if ( std::abs(gen.eta()) < minGenEta_ || std::abs(gen.eta()) > maxGenEta_ )
        continue;

      genPhotons.push_back(&gen);
    }

    nGenPhotons += genPhotons.size();
      
    for (auto& pho : event.photons) {
      if ( pho.scRawPt > maxPhoPt_ || pho.scRawPt < minPhoPt_ )
        continue;

      if ( std::abs(pho.eta()) > maxEta_ || std::abs(pho.eta()) < minEta_ )
        continue;

      pt = pho.pt();
      eta = pho.eta();
      phi = pho.phi();

      for (auto* gen : genPhotons) {
        if (gen->dR2(pho) < maxDR_ * maxDR_ &&
            std::abs(gen->pt() - pho.scRawPt) / gen->pt() < maxDPt_) {
          results[sMatch] = true;
          break;
        }
      }

      double pt2(pt * pt);
      //        double scEta(std::abs(pho.superCluster->eta));
      double scEta(std::abs(pho.eta()));

      switch (era_) {
      case Spring15:
        results[sHoverE] = pho.passHOverE(wp_, era_);
        results[sSieie] = pho.passSieie(wp_, era_);
        results[sNHIso] = pho.nhIsoS15 < panda::XPhoton::nhIsoCuts[era_][0][wp_];
        results[sPhIso] = pho.phIsoS15 < panda::XPhoton::phIsoCuts[era_][0][wp_];
        results[sCHIso] = pho.chIsoS15 < panda::XPhoton::chIsoCuts[era_][0][wp_];
        results[sCHMaxIso] = pho.chIsoMax < panda::XPhoton::chIsoCuts[era_][0][wp_];
        break;
      case Spring16:
        results[sHoverE] = pho.passHOverE(wp_, era_);
        results[sSieie] = pho.passSieie(wp_, era_);
        results[sNHIso] = pho.nhIso < panda::XPhoton::nhIsoCuts[era_][0][wp_];
        results[sPhIso] = pho.phIso < panda::XPhoton::phIsoCuts[era_][0][wp_];
        results[sCHIso] = pho.chIso < panda::XPhoton::chIsoCuts[era_][0][wp_];
        results[sCHMaxIso] = pho.chIsoMax < panda::XPhoton::chIsoCuts[era_][0][wp_];
        break;
      case Ashim_ZG_CWIso:
        results[sHoverE] = pho.hOverE < 0.0263;
        results[sSieie] = pho.sieie < 0.01002;
        results[sNHIso] = pho.nhIso + (0.0148 - 0.0112) * pt + (0.000017 - 0.000028) * pt2 < 7.005;
        results[sPhIso] = pho.phIso + (0.0047 - 0.0043) * pt < 3.271;
        results[sCHIso] = pho.chIso < 1.163;
        results[sCHMaxIso] = pho.chIsoMax - event.rho * (scEta < 1. ? 0.1064 : 0.1026) < 1.163;
        break;
      case Ashim_GJets_CIso:
        results[sHoverE] = pho.hOverE < 0.0232;
        results[sSieie] = pho.sieie < 0.00997;
        results[sNHIso] = pho.nhIso + (0.0148 - 0.0112) * pt + (0.000017 - 0.000028) * pt2 < 0.321;
        results[sPhIso] = pho.phIso + (0.0047 - 0.0043) * pt < 2.141;
        results[sCHIso] = pho.chIso < 0.584;
        results[sCHMaxIso] = true;
        break;
      default:
        break;
      }

      results[sEveto] = pho.pixelVeto;
      results[sSpike] = std::abs(pho.time) < 3. && pho.sieie > 0.001 && pho.sipip > 0.001 && !(pho.eta() > 0. && pho.eta() < 0.15 && pho.phi() > 0.527580 && pho.phi() < 0.541795);
      results[sHalo] = pho.mipEnergy < 4.9;

      output->Fill();
    }
  }

  _outputFile->cd();
  TObjString(TString::Format("gen=%d", nGenPhotons)).Write();

  return nGenPhotons;
}
