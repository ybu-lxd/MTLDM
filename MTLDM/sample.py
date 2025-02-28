import argparse
import os
import time
import einops
import numpy
import torch
import torch.optim as optim
import yaml
from torch.cuda.amp import GradScaler
from torch.amp import autocast
from ldm.models.mytoencoder import AutoencoderKL as AutoencoderKLVideo
from torch import nn
from ema_pytorch import EMA
from tqdm import tqdm

from utils_ import video_tensor_to_gif
from conditionlatentmodel import UNetModel as conditionUnetmodel
from ldm.mylatent import LatentDiffusion
from utils_ import Get_tager_sample_h5npy

import matplotlib.pyplot as plt


def main():
    batch_size = 1
    device = "cuda"
    scaler = GradScaler()
    with open('ldm/autoencoder_kl_32x32x4.yaml', 'r') as file:
        data = yaml.safe_load(file)
    train_1 = Get_tager_sample_h5npy("somedata.txt")
    auto_kl = AutoencoderKLVideo(data).to(device)
    
    auto_kl.load_state_dict(torch.load("Decoder-pre_weight/Autoencoder.pth",map_location=device))#
    
    
    #Here, you can select the appropriate decoder according to your needs. 
    # We provide decoder options for multiple rainfall thresholds, 
    # including 1mm/h, 4mm/h, 8mm/h and 4-8mm/h, as well as a comprehensive decoder covering all rainfall stages. 
    # These options can meet the needs of rainfall analysis in different scenarios.
    
    
    
    
    
    train_loader = torch.utils.data.DataLoader(train_1,
                                                batch_size = 1,
                                               pin_memory=True,
                                               num_workers=4,
                                               shuffle=True,
                                               )
    model = conditionUnetmodel(
                    image_size=32,
                    in_channels=32,
                    out_channels=4,
                    model_channels=192,
                    attention_resolutions=[1,2,4,8],
                    num_res_blocks=2,
                    channel_mult=[1,2,2,4,4],  # 32, 16, 8, 4, 2
                    num_heads=8,
                    use_scale_shift_norm=True,
                    resblock_updown=True,
                    time_atten=True,
                    use_netdown=True,
                    st=True,
                    transformer_merge = True,
                    use_latent = True
)
    net = LatentDiffusion(model=model,timesteps=1000,device=device,image_size=32,channels=4,batch_size=batch_size).to(device)
    net.load_state_dict(torch.load("diffusionpth/pre.pth"),state_dict=False) 
    #At the same time, we also provide the corresponding diffusion prediction weights
    #please note that your forecast image is rainfall rather than grayscale or reflectivity.
    (images_low,images_high,lable,name) = next(iter(train_loader))
    images_low = images_low.to(device)
    images_high = images_high.to(device)
    lable = lable.to(device)
    images_high =einops.rearrange(images_high,"b c f w h -> (b f) c w h")
    images_low = einops.rearrange(images_low,"b c f w h -> (b f) c w h")
    lable = einops.rearrange(lable,"b c f w h -> (b f) c w h")
    with autocast(device_type="cuda",dtype=torch.float16):
        with torch.no_grad():
            auto_kl.eval()
            images_high_latent = auto_kl(images_high)
    sampled_images = net.sample(batch_size=1,cond=[images_low,images_high_latent,images_high])
    sampled_images = einops.rearrange(sampled_images,"b c f w h ->(b f) c w h")
    sampled_images = sampled_images / 0.3788
    with torch.no_grad():
        sampled_images = auto_kl(sampled_images,False)# 32 32 4
    sampled_images = torch.clip(sampled_images,0,1)
    sampled_images = sampled_images*20.0
    sampled_images = einops.rearrange(sampled_images,"(b f) c w h  -> b c (f w) h",f=16)
    sampled_images = sampled_images[0,...]
    sampled_images = sampled_images.cpu().detach().numpy()
    plt.imshow(sampled_images)
    plt.show()
    
    
    
main()




