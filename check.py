import sys
sys.path.insert(0, '/home/tz-lom/sources/Resonance-PyProj')

import resonance

import numpy as np


si = resonance.si.Event(1, "foo")
db = resonance.db.Event(si, 1000, "hi")

print db

print np.size(db)

print db[0]+'kek'