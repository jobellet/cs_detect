
## install dependencies
import os

import torch

# to read .mat files
import mat4py

# to read .pkl files
import pandas as pd

# to do math operations
import numpy as np
import scipy.io as io
# To use the network
import uneye

# to get list of files
from glob import glob as dir

# to do dimensionality reduction
import umap

# to do unsupervised clustering
import hdbscan

# to plot things
from matplotlib import pyplot as plt 
from matplotlib.pyplot import *
matplotlib.style.use('classic')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# to perform signal processing
from scipy.signal import butter, lfilter
from scipy import signal as signal


# function selecting and concatenating together segments containing at least 1 compex spike
def concatenate_segments(LFP,HIGH,Interval_inspected,Labels):
    seg = Interval_inspected.copy()==1
    starts = np.where(np.concatenate(([0],np.diff(seg)==1)))[0]
    ends = np.where(np.concatenate(([0],np.diff(seg)==-1)))[0]
    if seg[-1] == 1:
        ends = np.concatenate(ends,len(seg)-1)
    for s,e in zip(starts,ends):
        if sum(labels[s:e])>0:
            print('found')
        else:
            seg[s:e] = False
    compLFP = LFP[seg]
    compHIGH = HIGH[seg]
    compLabels = Labels[seg]
    return (compLFP,compHIGH,compLabels)

def get_field_mat(data,fields): # go through structure in a .mat file to find the variable
    
    if len(fields) == 0:
        return([])
    if type(fields[0]) == list:
        for j in range(len(fields)): # if the variable can have different names
            try:
                data2 = data
                for i,subfield in enumerate(fields[j]):
                    data = data[subfield]
                return(data)
            except:
                print('trying an other field name')
                data = data2
    else:
        for i,field in enumerate(fields):
            data = data[field]
        return(data)
        
      
def get_field_pkl(df,field): # get the variable in a panda dataframe
    if field != None:
        data = np.array(df[field])
    else:
        data = None
    return(data)
  
  
def list2array(mylist): # convert a list into an array of segments of equal length
    if len(mylist) > 0:
        types = [hasattr(mylist[i],"__len__") for i in range(len(mylist))]
        if all(types) == 0: #surely a vector
            myarray = np.asarray(mylist)
        else:
            dur = [len(mylist[i]) for i in range(len(mylist))]
            mindur = min(dur)
            myarray = np.zeros((len(mylist),mindur))
            for i in range(len(mylist)):
                myarray[i,:] = mylist[i][:mindur]
    else:
        myarray = []
    return(myarray)
  

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def norm_LFP(LFP,sampling_freq): # normalise the LFP for the network
    if len(LFP) > 0:
        
        types = [hasattr(LFP[i],"__len__") for i in range(len(LFP))]
        if all(types) == 0 : #surely a vector
            LFP = np.asarray(LFP)
            
            b, a = butter_bandpass(30, 400, sampling_freq, order = 2)

            LFP =  signal.filtfilt(b, a, np.double(np.asarray(LFP))) 
            LFP /= np.median(np.abs(LFP))
            

        else:
            # normalise LFP as a multiple of absolute median
            b, a = butter_bandpass(30, 400, sampling_freq, order = 2)
            LFP = [signal.filtfilt(b, a, np.double(np.asarray(i))) for i in LFP ]
            LFP = [i/np.median(np.abs(i)) for i in LFP ]
    else:
        LFP = []     
    return(LFP)

def norm_high_pass(high_pass): # normalise the high pass signal for the network
    if len(high_pass) > 0:
        
        types = [hasattr(high_pass[i],"__len__") for i in range(len(high_pass))]
        if all(types) == 0 : #surely a vector
            high_pass = np.asarray(high_pass)
            high_pass = np.double(high_pass)
            high_pass /= np.median(np.abs(high_pass)) 

        else:
            # normalise high_pass as a multiple of absolute median
            high_pass = [i/np.median(np.abs(i)) for i in high_pass ]
    else:
        high_pass = []     
    return(high_pass)

       
def load_data(filename = [],field_LFP = [],field_high_pass = [], field_label = [],field_intervs = [],sampling_freq = 25000):
    # loads the data for .mat .pkl or .csv
    if len(filename) == 0:
        filename = field_LFP
    filename_start, file_extension = os.path.splitext(filename)
    if file_extension == '.pkl':
        df = pd.read_pickle(filename)
        LFP = list2array(norm_LFP(get_field_pkl(df,field_LFP),sampling_freq))
        high_pass = list2array(get_field_pkl(df,field_high_pass))
        Label = list2array(get_field_pkl(df,field_label))
        Intervs = list2array(get_field_pkl(df,field_intervs))
    elif file_extension == '.mat':
        data = mat4py.loadmat(filename)
        LFP = list2array(norm_LFP(get_field_mat(data,field_LFP),sampling_freq))
        high_pass = list2array(get_field_mat(data,field_high_pass))
        Label = list2array(get_field_mat(data,field_label))
        Intervs = list2array(get_field_mat(data,field_intervs))
    elif file_extension == '.csv':
        LFP = list2array(norm_LFP(np.loadtxt(field_LFP,delimiter=','),sampling_freq))
        high_pass = list2array(np.loadtxt(field_high_pass,delimiter=','))
        Label = list2array(np.loadtxt(field_label,delimiter=','))
        Intervs = list2array(np.loadtxt(field_intervs,delimiter=','))
    high_pass = norm_high_pass(high_pass) 
    return(LFP,high_pass,Label,Intervs)

def save_data(output_file,labels):
    filename_start, file_extension = os.path.splitext(output_file)
    if file_extension != '.mat':
        df = pd.DataFrame(columns = labels.keys())
        keys = list(labels.keys());
        for i in range(len(labels['cs_onset'])):
            temp1 = []
            for j in range(len(keys)):
                temp1.append(labels[keys[j]][i])
            temp = pd.DataFrame([temp1], columns=keys)
            df = df.append(temp)
    if file_extension == '.pkl': 
        df.to_pickle(output_file)
    elif file_extension == '.mat':
        io.savemat(output_file,labels)
    elif file_extension == '.csv':
        df.to_csv(output_file)
    elif file_extension == '.h5' :
        df.to_hdf(output_file, key='df', mode='w')
        
def nothingfound(output_name): # when no CS are found
    print('Warning : no complex spikes was found. Check your signals')
    labels = {'cs_onset': [],
                   'cs_offset': [],
                   'cluster_ID': [],
                 'embedding': []}
    if output_name != None:
        print('saving '+output_name)
        save_data(output_name,labels)
    return (labels)   
def detect_CS(weights_name, LFP, High_passed, output_name = None,  sampling_frequency = 25000, ks=9,mp=7, exlude_w = 3,realign = True, alignment_w = (-.5,2), cluster = True, cluster_w = (0,2),plot = False, plot_w= (-4,8),plot_only_good = True):
    # important arguments:
    # -filename is the filename path. If it is not defined then you should input the LFP and the High-passed signal
    # -weights_name is the path of the weight or just the name of the weight if it is stored in /training
    # -sampling_frequency is the sampling frequency of the signal analysed
    # ks and mp are the size of the kernel and max pooling operations respectively. 
    if plot:
        cmap = plt.get_cmap('jet')

    samp  = int(sampling_frequency/1000) # Khz
    
    if len(LFP)==0 or len(High_passed)==0: # if one signal is missing abort
        labels = nothingfound(output_name)
        return(labels)
    
    trial_length = 1 #sec, length per "trial"
    trial_length *= samp*1000
    if np.max(LFP.shape)>trial_length:
        # preprocessing: cut recording into overlapping pieces because the network can't deal with really big signals
        total_length = np.max(LFP.shape) #total recording length
        
        overlap = 0.1 #sec, length of overlap
        overlap *= samp*1000
        if np.floor(total_length/(trial_length-overlap))<(total_length-overlap)/(trial_length-overlap):
            num_steps = int(np.floor(total_length/(trial_length-overlap)))
        else:
            num_steps = int(np.floor(total_length/(trial_length-overlap)))-1
        steps = np.array([i*trial_length-i*overlap for i in range(num_steps)]).astype(int)
        LFP_mat = np.zeros((num_steps+1,trial_length))
        High_mat = np.zeros((num_steps+1,trial_length))
        
        for i,s in enumerate(steps):
            LFP_mat[i,:] = LFP[s:s+int(trial_length)]
            High_mat[i,:] = High_passed[s:s+int(trial_length)]
            
        # exception for last piece (from end-trial_length to end)
        LFP_mat[-1,:] = LFP[-int(trial_length):]
        High_mat[-1,:] = High_passed[-int(trial_length):]
        
        # normalise LFP as a multiple of absolute median
        for i in np.arange(0,np.shape(LFP_mat)[0]):
            LFP_mat[i,:] = LFP_mat[i,:]-np.median(LFP_mat[i,:])
            LFP_mat[i,:] = LFP_mat[i,:]/np.median(np.abs(LFP_mat[i,:]))
    else:
        LFP_mat = LFP
        High_mat = High_passed
    # U'n'Eye
    model = uneye.DNN(ks=ks,mp=mp,weights_name=weights_name,sampfreq=sampling_frequency,min_sacc_dur=1,doDiff = False)
    Pred,Prob = model.predict(LFP_mat,High_mat)
    
    if np.max(LFP.shape)>trial_length:
        # recover original shape
        Prediction = np.zeros(total_length)
        Probability = np.zeros(total_length)
        for i,s in enumerate(steps):
            if i==0:
                Prediction[s:s+int(trial_length)-int(overlap/2)] = Pred[i,:-int(overlap/2)]
                Probability[s:s+int(trial_length)-int(overlap/2)] = Prob[i,1,:-int(overlap/2)]
            else:
                Prediction[s+int(overlap/2):s+int(trial_length)-int(overlap/2)] = Pred[i,int(overlap/2):-int(overlap/2)]
                Probability[s+int(overlap/2):s+int(trial_length)-int(overlap/2)] = Prob[i,1,int(overlap/2):-int(overlap/2)]
        # exception for last piece
        Prediction[-int(trial_length)+int(overlap/2):] = Pred[-1,int(overlap/2):]
        Probability[-int(trial_length)+int(overlap/2):] = Prob[-1,1,int(overlap/2):]
    else:
        Prediction = Pred
        Probability = Prob
    cs_onset=np.argwhere(np.diff(Prediction)==1);
    cs_offset=np.argwhere(np.diff(Prediction)==-1);
    cs_onset = np.concatenate(cs_onset)
    cs_offset = np.concatenate(cs_offset)
    cs_offset = cs_offset[cs_offset>cs_onset[0]]
    cs_onset = cs_onset[cs_onset<cs_offset[-1]]
    if cluster ==False & realign==False: # stop early if everything that is needed is the raw output from the network
        labels = {'cs_onset':cs_onset,
                   'cs_offset':cs_offset}
        if output_name != None:
            print('saving '+output_name)
            save_data(output_name,labels) 
        return(labels)
    
    alignment_window = (np.array([sampling_frequency*alignment_w[0],sampling_frequency*alignment_w[1]])/1000).astype(int) # 2 ms to realign CS onset
    cluster_window = (np.array([sampling_frequency*cluster_w[0],sampling_frequency*cluster_w[1]])/1000).astype(int)  # consider the first 2 ms after CS onset for clustering
    plot_window = (np.array([sampling_frequency*plot_w[0],sampling_frequency*plot_w[1]])/1000).astype(int) # plot between 4 ms before and 8 ms after CS onset
    
    veto_wind = sampling_frequency*[0,0]
    if cluster:
        veto_wind =  [min(veto_wind[0],cluster_window[0]),max(veto_wind[1],cluster_window[1])]
    if realign:
        veto_wind =  [min(veto_wind[0],alignment_window[0]),max(veto_wind[1],alignment_window[1])]
    veto_wind = [min(plot_window[0],veto_wind[0]),max(plot_window[1],veto_wind[1])]
    
    # remove CSs detected to close from the edges of the signal
    not_too_close = np.logical_and((cs_onset>-veto_wind[0]),(cs_offset<len(Prediction)-veto_wind[1]))
    cs_offset = cs_offset[not_too_close]
    cs_onset = cs_onset[not_too_close]

    if len(cs_onset) == 0:
        labels = nothingfound(output_name)
        return(labels)
    
    ######################################## 
    # post processing
    ########################################
    
    
    # align each complex spike to the overall average
    
    average_CS = np.zeros((len(cs_onset),alignment_window[1]-alignment_window[0]))
    for i,j in enumerate(cs_onset):
        average_CS[i,:]=High_passed[j+alignment_window[0]:j+alignment_window[1]]
    
    norm_signal = np.median(np.abs(High_passed))/0.6745
    corrected_on=np.zeros((len(cs_onset),1))
    
    if realign:
        for i,j in enumerate(cs_onset):
            c=np.correlate(np.mean(average_CS,axis=0),average_CS[i,:],"full")
            lag = (np.argmax(c)-c.size/2)+.5
            corrected_on[i]=int(j-lag)
    else:     
        corrected_on = cs_onset
      
    if cluster == False: # if only the realignment of onsets was needed
        cs_onset = corrected_on
        labels = {'cs_onset':cs_onset,
                 'cs_offset':cs_offset}
        if output_name != None:
            print('saving '+output_name)
            save_data(output_name,labels) 
        return(labels)
    
    average_CS2 = np.zeros((len(cs_onset),cluster_window[1]-cluster_window[0])) 
    for i,j in enumerate(corrected_on):
        ind = int(j)
        average_CS2[i,:] = High_passed[ind+cluster_window[0]:ind+cluster_window[1]]
    
    average_prob = np.zeros((len(cs_onset),plot_window[1]-plot_window[0]))
    for i,j in enumerate(corrected_on):
        ind = int(j)
        average_prob[i,:] = Probability[ind+plot_window[0]:ind+plot_window[1]]
        
    average_LFP = np.zeros((len(cs_onset),cluster_window[1]-cluster_window[0]))
    for i,j in enumerate(corrected_on):
        ind = int(j)
        average_LFP[i,:] = LFP[ind+cluster_window[0]:ind+cluster_window[1]]
        
    if plot:
        average_CS_plot = np.zeros((len(cs_onset),plot_window[1]-plot_window[0]))
        for i,j in enumerate(cs_onset):
            ind = int(j)
            average_CS_plot[i,:]=High_passed[ind+plot_window[0]:ind+plot_window[1]]
        average_CS2_plot = np.zeros((len(cs_onset),plot_window[1]-plot_window[0]))
        for i,j in enumerate(corrected_on):
            ind = int(j)
            average_CS2_plot[i,:]=High_passed[ind+plot_window[0]:ind+plot_window[1]]
        average_LFP_plot = np.zeros((len(cs_onset),plot_window[1]-plot_window[0]))
        for i,j in enumerate(corrected_on):
            ind = int(j)
            average_LFP_plot[i,:] = LFP[ind+plot_window[0]:ind+plot_window[1]]
        
        
        u = np.random.permutation(i)[:np.round(i/2).astype(int)]
        fig = plt.figure()
        ax1 = plt.subplot(411)
        ax2 = plt.subplot(412)
        for z in u:
            ax1.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,average_CS_plot[z,:],c = 'k',Linewidth = 0.1)
            ax2.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,average_CS2_plot[z,:],c = 'k',Linewidth = 0.1)
        plt.show()
        #fig.savefig('realignment.pdf')
    # dimensionality reduction using UMAP
    n_neighbors = 15
    if np.shape(average_CS2)[0]<n_neighbors: # exit if the number of complex spike detected is too small
        labels = nothingfound(output_name)
        return(labels)
    
    embedding = umap.UMAP(n_neighbors = n_neighbors , min_dist=0.00001) 
    embedding = embedding.fit_transform(np.concatenate((average_CS2, average_LFP), axis=1))

    # clustering
    clustering = hdbscan.HDBSCAN(allow_single_cluster=True)
    clustering = clustering.fit(embedding)
    
    
    # keep all cluster of waveforms for which the average predictive probability lasts at least "exlude_w" ms
      
    tree = clustering.single_linkage_tree_.to_pandas()
    penultimate = np.sort(tree['size'])[-3]
    last = np.sort(tree['size'])[-2]
    distance =np.concatenate((np.array(tree['distance'][tree['size']==penultimate]), np.array(tree['distance'][tree['size']==last])), axis=None).mean()
    labels_big = clustering.single_linkage_tree_.get_clusters(distance,min_cluster_size=0)
    
    
    include = np.zeros((1,len(cs_onset))).astype(bool)[0]
    good_CS = []
    if plot:
        colors = cmap(np.linspace(0, 1.0, len(np.unique(labels_big))))
        fig = plt.figure()
        ax0 = plt.subplot(311)
        ax1 = plt.subplot(312)
        ax2 = plt.subplot(313)
    for i,lab in enumerate(np.unique(labels_big)):
        good_CS.append((sum((np.mean(average_prob[labels_big==lab,:],axis = 0)>.5).astype(float))/samp)>exlude_w)
        if good_CS[i]:
            include[labels_big==lab] = True
        if plot:
            if plot_only_good == True:
                if good_CS[i]:
                    u = np.argwhere(labels_big==lab)
                    u = np.random.permutation(u)[:np.round(len(u)/2).astype(int)]
                    for z in u:
                        ax1.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,average_CS2_plot[z[0],:],c = colors[i], Linewidth = 0.1)
                        ax0.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,average_LFP_plot[z[0],:],c = colors[i], Linewidth = 0.1)
                        ax0.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,
                                  np.mean(average_LFP_plot[labels_big==lab,:],axis = 0),c = colors[i])
                   
                    ax1.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,
                             np.mean(average_CS2_plot[labels_big==lab,:],axis = 0),c = colors[i])
                    ax2.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,np.mean(average_prob[labels_big==lab,:],axis = 0), c = colors[i])
            else:
                u = np.argwhere(labels_big==lab)
                u = np.random.permutation(u)[:np.round(len(u)/2).astype(int)]
                for z in u:
                    ax1.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,average_CS2_plot[z[0],:],c = colors[i],Linewidth = 0.1)
                    ax0.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,average_LFP_plot[z[0],:],c = colors[i],Linewidth = 0.1)
                
                ax0.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,
                         np.mean(average_LFP_plot[labels_big==lab,:],axis = 0),c = colors[i])
                ax1.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,
                         np.mean(average_CS2_plot[labels_big==lab,:],axis = 0),c = colors[i])
                ax2.plot(np.arange(plot_window[0],plot_window[1])/sampling_frequency*1000,
                         np.mean(average_prob[labels_big==lab,:],axis = 0),c = colors[i])
                  
    if plot:    
        xlabel('time from CS onset (ms)',fontsize=15)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.set_facecolor('none')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.set_facecolor('none')
        ax2.axis(ymin=0,ymax=1.01)
        plt.show()
    for i,lab in enumerate(np.unique(labels_big)):
        if plot:
            if plot_only_good == True:
                if good_CS[i]:
                    plt.scatter(embedding[labels_big==lab,0],embedding[labels_big==lab,1],c = colors[i], edgecolors = 'face')
            else:
                plt.scatter(embedding[labels_big==lab,0],embedding[labels_big==lab,1],c = colors[i], edgecolors = 'face')
    cs_onset = corrected_on[include];
    cs_offset = cs_offset[include]
    
    cs_onset = cs_onset.astype('int')
    try: 
        cs_onset = np.concatenate(cs_onset)
    except: # some times no complex spikes end up being detected
        labels = nothingfound(output_name)
        return(labels)
    cs_offset = cs_offset.astype('int')

    labels = {'cs_onset':cs_onset,
               'cs_offset':cs_offset,
               'cluster_ID': labels_big[include],
             'embedding': embedding[include,:]}
    if output_name != None:
        print('saving '+output_name)
        save_data(output_name,labels)
    return(labels)
    
    
    
