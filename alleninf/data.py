from glob import glob
import os
import pandas as pd
import numpy as np
import nibabel as nb
import numpy.linalg as npl

#code from neurosynth
def get_sphere(coords, r, vox_dims, dims):
    """ # Return all points within r mm of coordinates. Generates a cube
    and then discards all points outside sphere. Only returns values that
    fall within the dimensions of the image."""
    r = float(r)
    xx, yy, zz = [slice(-r / vox_dims[i], r / vox_dims[
                        i] + 0.01, 1) for i in range(len(coords))]
    cube = np.vstack([row.ravel() for row in np.mgrid[xx, yy, zz]])
    sphere = cube[:, np.sum(np.dot(np.diag(
        vox_dims), cube) ** 2, 0) ** .5 <= r]
    sphere = np.round(sphere.T + coords)
    return sphere[(np.min(sphere, 1) >= 0) & (np.max(np.subtract(sphere, dims), 1) <= -1),:].astype(int)

def read_donor_data(data_dir):
    donor_ids = [path.split(os.path.sep)[-2] for path in glob(os.path.join(data_dir, "*", "MicroarrayExpression.csv"))]
    print "Data directory contains the following donors: %s" % ", ".join(donor_ids)
    main_df = "empty"
    for donor_id in donor_ids:
        print "Reading data from donor %s"%donor_id
        sample_locations = pd.read_csv(os.path.join(data_dir, donor_id, 'SampleAnnot.csv'))
        df = pd.DataFrame([donor_id] * sample_locations.shape[0], columns=["donor_id"])
        expression_data = pd.read_csv(os.path.join(data_dir, donor_id, 'MicroarrayExpression.csv'), header=None, index_col=0)
        expression_data.columns = range(expression_data.shape[1])
        df = pd.concat([df, expression_data.T], axis=1, ignore_index=False)
        if isinstance(main_df, str):
            main_df = df
        else:
            main_df = pd.concat([main_df, df], ignore_index=True)
    return main_df

def get_values_at_locations(nifti_file, locations, radius, mask_file=None,  verbose=False):
    values = []
    nii = nb.load(nifti_file)
    data = nii.get_data()
    
    if mask_file:
        mask_data = nb.load(mask_file).get_data()
        mask = np.logical_and(np.logical_not(np.isnan(mask_data)), mask_data > 0)
    else:
        if verbose:
            print "No mask provided - using implicit (not NaN, not zero) mask"
        mask = np.logical_and(np.logical_not(np.isnan(data)), data != 0)
        
    for location in locations:
        coord_data = [round(i) for i in nb.affines.apply_affine(npl.inv(nii.get_affine()), location)]
        sph_mask = (np.zeros(mask.shape) == True)
        if radius:
            sph = tuple(get_sphere(coord_data, vox_dims=nii.get_header().get_zooms(),r=radius, dims=nii.shape).T)
            sph_mask[sph] = True
        else:
            #if radius is not set use a single point
            sph_mask[coord_data[0], coord_data[1], coord_data[2]] = True
        
        roi = np.logical_and(mask, sph_mask)
        
        #If the roi is outside of the statmap mask we should treat it as a missing value
        if np.any(roi):
            val = data[roi].mean()
        else:
            val = np.nan
        values.append(val)
    return values

def combine_expression_values(expression_values, method="average"):
    if method == "average":
        return list(np.array(expression_values).mean(axis=0))
    elif method == "pca":
        from sklearn.decomposition import TruncatedSVD
        pca = TruncatedSVD(n_components=1)
        pca.fit(np.array(expression_values))
        return list(pca.components_[0,:])
    else:
        raise Exception("Uknown method")

if __name__ == '__main__':
    data_dir='/Users/filo/Dropbox/papers/beyond_blobs/data/donors'
    df = read_donor_data(data_dir)
    print df.shape