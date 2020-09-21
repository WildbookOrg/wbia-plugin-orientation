# ------------------------------------------------------------------------------
# Licensed under the MIT License.
# Written by Olga Moskvyak (olga.moskvyak@hdr.qut.edu.au)
# ------------------------------------------------------------------------------
import math
import numpy as np

def compute_theta(coords):
    """
    Compute angle of orientation theta based on output coordinates.
    Input:
        coords: numpy array of shape (bs, 5) where each row is [xc, yc, xt, yt, w]
    Returns:
        theta_pred: numpy array of angle theta in radians
    """   
    theta_pred = np.arctan2(coords[:,3]-coords[:,1], coords[:,2]-coords[:,0])
    #Add 90 degrees to align arctan2 notation with annotations
    theta_pred += math.radians(90)
    
    return theta_pred    
    

def evaluate_orientaion(output, target_coords, target_theta, theta_thr = 10, theta_source = 'annot'):    
    '''
    Evaluate errors and accuracy of orientation detection.
    Input:
        output: numpy array of shape (bs, 5) where each row is [xc, yc, xt, yt, w]
        target: numpy array of shape (bs, 5), ground truth for [xc, yc, xt, yt, w]
        target_theta: array of shape (bs), ground truth for angle of orientation theta in radians (from annotations)
        theta_thr (int): threshold for error in degrees when theta detection is considered correct
        theta_source (string): 'annot' or 'calc', source of theta, get from ground truth annotations or calculate from gt coordinates.
            Arctan compute angle between provided vector and vector (1, 0).
            Theta in annotations is a different angle so we add 90 degrees to align to values.
    Returns:
        eval_dict (dictionary):
            'err_theta': mean error in degrees for angle theta
            'acc_theta': accuracy of theta prediction, prediction is correct if error is below threshold
            'err_xcyc': mean distance in pixels between ground truth and predictions for (xc, yc)
            'err_xtyt': mean distance in pixels between ground truth and predictions for (xt, yt)
            'err_w': mean distance in pixels between ground truth and predictions for w
    '''
    #Compute predicted truth theta (np.arctan2(yt-yc, xt-xc))
    theta_pred = np.arctan2(output[:,3]-output[:,1], output[:,2]-output[:,0])
    if theta_source == 'annot':
        theta_pred += math.radians(90)
    
    #Ground truth theta can be computed from ground truth (xc, yc) and (xt, yt) or taken directly from annotations
    if theta_source == 'annot':
        theta_gt = target_theta
    else:
        theta_gt = np.arctan2(target_coords[:,3]-target_coords[:,1], target_coords[:,2]-target_coords[:,0])
        
    #Comvert to angles
    theta_pred = np.rad2deg(theta_pred)
    theta_gt = np.rad2deg(theta_gt)
   
    np_normalize_theta = np.vectorize(normalize_theta)    
    err_theta = np.abs(np_normalize_theta(theta_pred) - np_normalize_theta(theta_gt))    
    acc_theta = (err_theta < theta_thr).sum() / len(theta_gt)
    
    err_xcyc = np.linalg.norm(target_coords[:, :2] - output[:, :2])
    err_xtyt = np.linalg.norm(target_coords[:, 2:4] - output[:, 2:4])
    err_w = np.abs(target_coords[:, 4] - output[:, 4])
    
    eval_dict = {
            'err_theta': np.mean(err_theta),
            'acc_theta': acc_theta,
            'err_xcyc': np.mean(err_xcyc),
            'err_xtyt': np.mean(err_xtyt),
            'err_w': np.mean(err_w),
            }
        
    return eval_dict

def normalize_theta(theta, degrees=True):
    '''Normalize angle theta to be between -180 and 180 degrees
    Input:
        theta (float): angle in degrees
        degrees (bool, default True): if True then theta in degrees else theta in radians
    '''
    if degrees:
        pi = 180.
    else:
        pi = math.pi
        
    if theta >= 2*pi or theta <= -2*pi:
        theta = theta % (2*pi) 
    
    if theta <= pi and theta > -pi:
        return theta
    
    elif theta > pi:
        theta -= 2*pi
        return theta
    
    else:
        theta += 2*pi
        return theta 
    


