"""Physical constants for ion transport in air, from Kanai et al. (1998).

One averaged mobility/diffusion pair for both carrier species -- the
original IonTracks-Cython model. A real dosimetry code resolves the two
species (positive/negative ions drift and diffuse at slightly different
rates) separately; this workshop version does not, to keep the physics
simple to read.
"""

W_EV_PER_ION_PAIR = 34.2  # eV, mean energy to create an ion pair in air (protons)
ION_MOBILITY_CM2_VS = 1.65  # cm^2 / (V s), averaged over positive/negative ions
ION_DIFFUSION_CM2_S = 3.7e-2  # cm^2 / s, averaged over positive/negative ions
RECOMBINATION_ALPHA_CM3_S = 1.60e-6  # cm^3 / s, recombination coefficient

AIR_DENSITY_KG_M3 = 1.225  # dry air, standard conditions (ISA sea level)
JOULE_TO_KEV = 6.241e15  # 1 J expressed in keV

DEFAULT_BUFFER_RADIUS = 4  # voxels of margin around the sampled cylinder
DEFAULT_NO_Z_ELECTRODE = 3  # voxels of margin at each electrode
