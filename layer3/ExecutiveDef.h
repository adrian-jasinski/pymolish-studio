#pragma once

#include <unordered_map>

#include "Ortho.h"

class SpecRec;
class CGO;
struct CTracker;
struct OVLexicon;

struct ExecutiveObjectOffset{
  ObjectMolecule *obj;
  int atm;
};



struct ListMember{
  int list_id;
  int next;
};

struct CExecutive : public Block {
  SpecRec *Spec {};
  CTracker *Tracker {};
  pymol::CObject *LastEdited { nullptr };
  int all_names_list_id {}, all_obj_list_id {}, all_sel_list_id {};
  OVLexicon *Lex {};
  std::unordered_map<ov_word, int> Key;
  bool ValidGroups { false };
  bool ValidSceneMembers { false };
  int ValidGridSlots {};

  int CaptureFlag {};
  int LastMotionCount {};
  CGO *selIndicatorsCGO { nullptr };
  int selectorTexturePosX { 0 }, selectorTexturePosY { 0 }, selectorTextureAllocatedSize { 0 }, selectorTextureSize { 0 };
  short selectorIsRound { 0 };

  // AtomInfoType::unique_id -> (object, atom-index)
  std::vector<ExecutiveObjectOffset> m_eoo {}; // vector of (object, atom-index)
  std::unordered_map<ov_word, std::size_t> m_id2eoo {}; // unique_id -> m_eoo-index
  std::unordered_map<const pymol::CObject*, std::unordered_set<const pymol::CObject*>> m_objDeps;

  CExecutive(PyMOLGlobals * G) : Block(G) {};

};
