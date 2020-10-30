import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
import batchminer
from geomloss import SamplesLoss
"""================================================================================================="""
ALLOWED_MINING_OPS  = list(batchminer.BATCHMINING_METHODS.keys())
REQUIRES_BATCHMINER = True
REQUIRES_OPTIM      = False

### Standard Triplet Loss, finds triplets in Mini-batches.
class Criterion(torch.nn.Module):
    def __init__(self, opt, batchminer):
        super(Criterion, self).__init__()
        self.margin     = opt.loss_triplet_margin
        self.batchminer = batchminer
        self.name           = 'wtriplet'
        ####
        self.ALLOWED_MINING_OPS  = ALLOWED_MINING_OPS
        self.REQUIRES_BATCHMINER = REQUIRES_BATCHMINER
        self.REQUIRES_OPTIM      = REQUIRES_OPTIM
    def triplet_distance(self, anchor, positive, negative):
 #       return torch.nn.functional.relu((anchor-positive).pow(2).sum()-(anchor-negative).pow(2).sum()+self.margin)
         wloss = SamplesLoss("sinkhorn", p=2, blur=0.05, scaling=.99, backend="online")
         loss1 = wloss(torch.Tensor(anchor),torch.Tensor(positive))
         loss2 = wloss(torch.Tensor(anchor),torch.Tensor(negative))
         return torch.nn.functional.relu(loss1 - loss2  + self.margin)
    def forward(self, batch, labels, **kwargs):
        if isinstance(labels, torch.Tensor): labels = labels.cpu().numpy()
        sampled_triplets = self.batchminer(batch, labels)
        loss             = torch.stack([self.triplet_distance(batch[triplet[0],:],batch[triplet[1],:],batch[triplet[2],:]) for triplet in sampled_triplets])

        return torch.mean(loss)