import pylab as plt
import seaborn as sns
import numpy as np
from scipy.stats.stats import pearsonr, ttest_1samp, percentileofscore,\
    linregress

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
        correlation_per_donor[donor_id], _, _, _, _ = linregress(list(data[labels[0]][data[group] == donor_id]),
                                                       list(data[labels[1]][data[group] == donor_id]))
    average_slope = np.array(correlation_per_donor.values()).mean()
    t, p_val = ttest_1samp(correlation_per_donor.values(), 0)
    print "Averaged slope across donors = %g (t=%g, p=%g)"%(average_slope, t, p_val)
    sns.violinplot([correlation_per_donor.values()], inner="points", names=["donors"])
    plt.ylabel("Linear regression slopes between %s and %s"%(labels[0],labels[1]))
    plt.axhline(0, color="red")
    
    sns.lmplot(labels[0], labels[1], data, hue=group, col=group, col_wrap=3)
    plt.show()
    
    return average_slope, t, p_val

def bayesian_random_effects(data, labels, group, n_samples=2000, n_burnin=500):
    import pymc as pm
    #preparing the data
    donors = data[group].unique()
    donors_lookup = dict(zip(donors, range(len(donors))))
    data['donor_code'] = data[group].replace(donors_lookup).values
    n_donors = len(data[group].unique())
    donor_idx = data['donor_code'].values
    
    #setting up the model
    with pm.Model() as hierarchical_model:
        # Hyperpriors for group nodes
        group_intercept_mean = pm.Normal('group intercept (mean)', mu=0., sd=100**2)
        group_intercept_variance = pm.Uniform('group intercept (variance)', lower=0, upper=100)
        group_slope_mean = pm.Normal('group slope (mean)', mu=0., sd=100**2)
        group_slope_variance = pm.Uniform('group slope (variance)', lower=0, upper=100)
        
        individual_intercepts = pm.Normal('individual intercepts', mu=group_intercept_mean, sd=group_intercept_variance, shape=n_donors)
        individual_slopes = pm.Normal('individual slopes', mu=group_slope_mean, sd=group_slope_variance, shape=n_donors)
        
        # Model error
        residuals = pm.Uniform('residuals', lower=0, upper=100)
        
        expression_est =  individual_slopes[donor_idx] * data[labels[0]].values + individual_intercepts[donor_idx]
        
        # Data likelihood
        expression_like = pm.Normal('expression_like', mu=expression_est, sd=residuals, observed=data[labels[1]])

        start = pm.find_MAP()
        step = pm.NUTS(scaling=start)
        hierarchical_trace = pm.sample(n_samples, step, start=start, progressbar=True)
        
    mean_slope = hierarchical_trace['group slope (mean)'][n_burnin:].mean()
    zero_percentile = percentileofscore(hierarchical_trace['group slope (mean)'][n_burnin:], 0)
    print "Mean group level slope was %g (zero was %g percentile of the posterior distribution)"%(mean_slope, zero_percentile)
    
    pm.summary(hierarchical_trace[n_burnin:], vars=['group slope (mean)'])
        
    pm.traceplot(hierarchical_trace[n_burnin:])
    
    selection = donors
    fig, axis = plt.subplots(2, 3, figsize=(12, 6), sharey=True, sharex=True)
    axis = axis.ravel()
    xvals = np.linspace(data[labels[0]].min(), data[labels[0]].max())
    for i, c in enumerate(selection):
        c_data = data.ix[data[group] == c]
        c_data = c_data.reset_index(drop = True)
        z = list(c_data['donor_code'])[0]
        for a_val, b_val in zip(hierarchical_trace['individual intercepts'][n_burnin::10][z], hierarchical_trace['individual slopes'][n_burnin::10][z]):
            axis[i].plot(xvals, a_val + b_val * xvals, 'g', alpha=.1)
        axis[i].plot(xvals, hierarchical_trace['individual intercepts'][n_burnin:][z].mean() + hierarchical_trace['individual slopes'][n_burnin:][z].mean() * xvals, 
                     'g', alpha=1, lw=2.)
        axis[i].hexbin(c_data[labels[0]], c_data[labels[1]], mincnt=1, cmap=plt.cm.YlOrRd_r)
        axis[i].set_title(c)
        axis[i].set_xlabel(labels[0])
        axis[i].set_ylabel(labels[1])
        
    plt.show()
        
    return mean_slope, zero_percentile