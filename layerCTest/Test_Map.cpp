#include <cmath>
#include <random>
#include <set>

#include "Test.h"

#include "Map.h"
#include "Vector.h"

using namespace pymol;

/* The list MapSetupExpress files under a point holds every point within the
   cutoff of it, once, and ends with -1. */
static void check_neighbor_lists(PyMOLGlobals* G, int n)
{
  const float cutoff = 1.5F;
  std::mt19937 gen(n);
  std::uniform_real_distribution<float> coord(0.F, std::cbrt(float(n)));
  std::vector<float> v(3 * n);
  for (auto& x : v)
    x = coord(gen);

  MapType map(G, cutoff, v.data(), n, nullptr);
  REQUIRE(MapSetupExpress(&map));

  int missing = 0, repeated = 0;
  for (int a = 0; a < n; a += n / 100) {
    const float* va = v.data() + 3 * a;
    std::set<int> listed;
    int i = *MapLocusEStart(&map, va);
    REQUIRE(i > 0);
    for (int j = map.EList[i]; j >= 0; j = map.EList[++i])
      repeated += !listed.insert(j).second;
    for (int j = 0; j < n; j++)
      if (within3f(v.data() + 3 * j, va, cutoff))
        missing += !listed.count(j);
  }
  REQUIRE(missing == 0);
  REQUIRE(repeated == 0);
}

TEST_CASE("MapSetupExpress lists every neighbor", "[Map]")
{
  PyMOLInstance pymol;
  check_neighbor_lists(pymol.G(), 500);   // one thread
  check_neighbor_lists(pymol.G(), 20000); // above the threading threshold
}
