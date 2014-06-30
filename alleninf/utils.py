import os
import pandas as pd
import numpy as np
from glob import glob

def allen_csv_to_hdf(donors_dir, hdf_output='data/microarray_expression.h5'):
    """Takes a directory with one subdirectory for each donor containing a
    SampleAnnot.csv and MicroarrayExpression.csv files. The output is a 
    compressed HDF5 file containing concatenated wells x gene probes table."""
    
    donor_ids = [p.split(os.sep)[-1] for p in glob(os.path.join(data_dir, "*"))]

    for donor_id in donor_ids:
        print "adding donor %s"%donor_id
        sample_locations = pd.read_csv(os.path.join(data_dir, 
                donor_id, 'SampleAnnot.csv'))
        df = pd.DataFrame({"well_id":list(sample_locations.well_id)})
        expression_data = pd.read_csv(os.path.join(data_dir, 
                donor_id, 
                'MicroarrayExpression.csv'), 
            header=None, index_col=0, dtype=np.float32)
        expression_data.columns = range(expression_data.shape[1])
        df = pd.concat([df, expression_data.T], axis=1, ignore_index=False)
        df.set_index("well_id", inplace=True)
        df = df.transpose()
        
        df.columns = ["well_id_" + str(int(c)) for c in df.columns]
        df.index = [int(c) for c in df.index]
        df.index.name = 'probe_id'
        df.to_hdf(hdf_output, donor_id, mode="a", format='table', complevel=9, complib='blosc')

if __name__ == '__main__':
    data_dir='../../../papers/beyond_blobs/data/donors'
    allen_csv_to_hdf(data_dir)
