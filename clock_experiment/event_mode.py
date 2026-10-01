"""Constant-frequency candidate and frozen-phase event score."""
import numpy as np

def fit_mode(t,grid):
    t=np.asarray(t,float)
    phasors=np.exp(2j*np.pi*np.outer(grid,t))
    mean=phasors.mean(axis=1); k=int(np.argmax(abs(mean)))
    return float(grid[k]),float(np.angle(mean[k])),float(abs(mean[k]))

def score_mode(t,f,phase):
    return float(np.mean(np.cos(2*np.pi*f*np.asarray(t)-phase)))
