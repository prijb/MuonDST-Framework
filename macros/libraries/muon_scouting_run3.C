//
// LIBRARY FOR SNT SCOUTING DIMUON ANALYSIS
// @fernance (25 Jul 2023)
//


// Function to make dimuon vertices out of the associated muons
// OS muon pairs
/*
auto MakeDimuonVertices(ROOT::RVec<int> SVOv, ROOT::RVec<int> SV, ROOT::RVec<int> ch) {
  int ovidx;
  int vidx;
  ROOT::RVec<int> dmuidxs;
  for (int m = 0; m < ch.size(); m++) {
    ovidx = -1;
    vidx = -1;
    if (SVOv.at(m) > -1) {
      ovidx = SVOv.at(m);
    } else if (SV.at(m) > -1) { 
      vidx = SV.at(m);
    }
    for (int mm = 0; mm < ch.size(); mm++) {
      if (m==mm) continue;
      if (ch.at(m)*ch.at(mm) > 0) continue;
        if ( !(ovidx > -1 && ovidx == SVOv.at(mm)) && vidx > -1 && vidx == SV.at(mm)) {
        if (!(std::find(dmuidxs.begin(), dmuidxs.end(), m) != dmuidxs.end() || std::find(dmuidxs.begin(), dmuidxs.end(), mm) != dmuidxs.end())) {
          dmuidxs.push_back(m);
          dmuidxs.push_back(mm);
        }
      }
    }
  }
  return dmuidxs;
}
*/

// Function to compute invariant mass from vector of TLorentzVectors
/*
auto GetVectorMass(ROOT::RVec<TLorentzVector> x) {
  ROOT::RVec<double> mass;
  for (auto m:x)
    mass.push_back(m.M());
  return mass;
}
*/

// Function to create a new RVec from selected RVec indexes
template <typename TYPE>
inline auto GetElements(ROOT::RVec<TYPE> v, ROOT::RVec<int> idx) {
  ROOT::RVec<TYPE> out;
  for (auto x:idx)
    out.push_back(v.at(x));
  return out;
}

// Function to compute invariant mass from vector of TLorentzVectors
auto GetTLorentzVector(ROOT::RVec<double> pt, ROOT::RVec<double> eta, ROOT::RVec<double> phi, double mass) {
  ROOT::RVec<TLorentzVector> x;
  for (int i = 0; i < pt.size(); i++) {
    TLorentzVector v;
    v.SetPtEtaPhiM(pt.at(i), eta.at(i), phi.at(i), mass);
    x.push_back(v);
  }
  return x;
}

// Function to perform muon matching
auto GetMatchedObjects(ROOT::RVec<int> idx, ROOT::RVec<TLorentzVector> vec1, ROOT::RVec<TLorentzVector> vec2) {
  ROOT::RVec<int> matched_idx;
  for (int i = 0; i < idx.size(); i++) {
    double min_dR = 99999;
    int min_idx = 99999;
    for (int j = 0; j < vec2.size(); j++) {
       if (std::find(matched_idx.begin(), matched_idx.end(), j) != matched_idx.end())
         continue;
       if (vec1.at(idx.at(i)).DeltaR(vec2.at(j)) < min_dR) {
         min_dR = vec1.at(idx.at(i)).DeltaR(vec2.at(j));
         min_idx = j;
       }
    }
    if (min_dR < 0.2)
      matched_idx.push_back(min_idx);
    else
      matched_idx.push_back(-9);
  }
  return matched_idx;
}

// Function to prune the pairs that are not reconstructed
auto PruneDimuonPairs(ROOT::RVec<int> idx, ROOT::RVec<int> comp) {
  ROOT::RVec<int> out;
  for (int i = 0; i < idx.size(); i+=2) {
    if ((comp.at(i) > -1) && (comp.at(i+1) > -1)) {
      out.push_back(idx.at(i));
      out.push_back(idx.at(i+1));
    }
  }
  return out;
}

// Function to make dimuon pairs
// Returns a vector with muon indexes
auto GetDimuonPairs(ROOT::RVec<int> charge, ROOT::RVec<TLorentzVector> vec, float minPt) {
  ROOT::RVec<int> out;
  for (int i = 0; i < charge.size(); i++) {
    if (std::find(out.begin(), out.end(), i) != out.end())
      continue;
    if (vec.at(i).Pt() < minPt || fabs(vec.at(i).Eta()) > 2.4)
      continue;
    for (int j= i+1; j < charge.size(); j++) {
      if (std::find(out.begin(), out.end(), j) != out.end())
        continue;
      if (vec.at(j).Pt() < minPt || fabs(vec.at(j).Eta()) > 2.4)
        continue;
      if (charge.at(i)*charge.at(j) < 0.0 && vec.at(i).DeltaR(vec.at(j)) > 0.2) {
        if (vec.at(i).Pt() > vec.at(j).Pt()) {
          out.push_back(i);
          out.push_back(j);
        } else {
          out.push_back(j);
          out.push_back(i);
        }
      }
    }
  }
  return out;
}

// Function to get dimuon mass
auto GetDimuonMass(ROOT::RVec<int> idx, ROOT::RVec<TLorentzVector> x) {
  ROOT::RVec<double> mass;
  for (int i = 0; i < idx.size(); i+=2) {
    mass.push_back( ( x.at(idx.at(i)) + x.at(idx.at(i+1)) ).M() );
  }
  return mass;
}
