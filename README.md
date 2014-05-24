alleninf
========

Compare a statistical map of a brain with gene expression patterns from Allen Human Brain Atlas.


usage: alleninf [-h] [--inference_method INFERENCE_METHOD]
                [--probes_reduction_method PROBES_REDUCTION_METHOD]
                [--mask MASK] [--radius RADIUS]
                stat_map gene_name

Compare a statistical map with gene expression patterns from Allen Human Brain
Atlas.

positional arguments:
  stat_map              Statistical map in the form of a 3D NIFTI file (.nii
                        or .nii.gz) in MNI space.
  gene_name             Name of the gene you want to compare your map with.
                        For list of all available genes see: http://help
                        .brain-map.org/download/attachments/2818165/HBA_ISH_Ge
                        neList.pdf?version=1&modificationDate=1348783035873.

optional arguments:
  -h, --help            show this help message and exit
  --inference_method INFERENCE_METHOD
                        Which model to use: fixed - fixed effects,
                        approximate_random - approximate random effects
                        (default).
  --probes_reduction_method PROBES_REDUCTION_METHOD
                        How to combine multiple probes: average (default) or
                        pca - use first principal component.
  --mask MASK           Explicit mask for the analysis in the form of a 3D
                        NIFTI file (.nii or .nii.gz) in the same space and
                        dimensionality as the stat_map. If not used an
                        implicit mask (non zero and non NaN voxels) will be
                        used.
  --radius RADIUS       Radius in mm of of the sphere used to average
                        statistical values at the location of each
                        probe.(default: 4mm).

