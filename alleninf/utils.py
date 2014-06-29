import os
import pandas as pd
import numpy as np
from glob import glob

def allen_csv_to_hdf(donors_dir, hdf_output='data/microarray_expression.h5'):
    """Takes a directory with one subdirectory for each donor containing a
    SampleAnnot.csv and MicroarrayExpression.csv files. The output is a 
    compressed HDF5 file containing concatenated wells x gene probes table."""
    
    donor_ids = [p.split(os.sep)[-1] for p in glob(os.path.join(data_dir, "*"))]
    main_df = "empty"
    for donor_id in donor_ids:
        sample_locations = pd.read_csv(os.path.join(data_dir, 
                donor_id, 'SampleAnnot.csv'))
        df = pd.DataFrame({"donor_id":[donor_id] * sample_locations.shape[0], 
                "well_id":list(sample_locations.well_id)})
        expression_data = pd.read_csv(os.path.join(data_dir, 
                donor_id, 
                'MicroarrayExpression.csv'), 
            header=None, index_col=0, dtype=np.float32)
        expression_data.columns = range(expression_data.shape[1])
        df = pd.concat([df, expression_data.T], axis=1, ignore_index=False)
        if isinstance(main_df, str):
            main_df = df
        else:
            main_df = pd.concat([main_df, df], ignore_index=True)
    
    main_df.columns = list(main_df.columns[0:2]) + [str(int(c)) for c in main_df.columns[2:]]
    main_df.set_index("well_id", inplace=True)
    main_df.to_hdf(hdf_output, 'table', complevel=9, complib='blosc')

if __name__ == '__main__':
    data_dir='../../../papers/beyond_blobs/data/donors'
    allen_csv_to_hdf(data_dir)
