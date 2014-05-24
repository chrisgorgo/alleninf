import pylab as plt
import seaborn as sns
import numpy as np
from scipy.stats.stats import pearsonr, ttest_1samp

def fixed_effects(data, labels):
    
    corcoeff, p_val = pearsonr(data[labels[0]], data[labels[1]])
    print "Pearson correlation between %s and %s across all donors is %g (two tailed p value = %g)"%(labels[0], labels[1], corcoeff, p_val)
    
    grid = sns.jointplot(labels[0], labels[1], data, kind="hex")
    sns.jointplot(labels[0], labels[1], data, kind="reg", 
                         xlim=grid.ax_joint.get_xlim(),
                         ylim=grid.ax_joint.get_ylim())
    plt.show()
    
    return corcoeff, p_val

def approximate_random_effects(data, labels, group):

    correlation_per_donor = {}
    for donor_id in set(data[group]):
        correlation_per_donor[donor_id],_ = pearsonr(list(data[labels[0]][data[group] == donor_id]),
                                                 list(data[labels[1]][data[group] == donor_id]))
    average_correlation = np.array(correlation_per_donor.values()).mean()
    t, p_val = ttest_1samp(correlation_per_donor.values(), 0)
    print "Correlation between %s and %s averaged across donors = %g (t=%g, p=%g)"%(labels[0],labels[1],
                                                                                    average_correlation,
                                                                                    t, p_val)
    sns.violinplot([correlation_per_donor.values()], inner="points", names=["donors"])
    plt.ylabel("Correlation between %s and %s"%(labels[0],labels[1]))
    plt.axhline(0, color="red")
    
    sns.lmplot(labels[0], labels[1], data, hue=group, col=group, col_wrap=3)
    plt.show()
    
    return average_correlation, t, p_val