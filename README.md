# MTLDM




# HOW TO USE?

```
auto_kl.load_state_dict(torch.load("Decoder-pre_weight/Autoencoder.pth",map_location=device))#
``` 
    
Here, you can select the appropriate decoder according to your needs. We provide decoder options for multiple rainfall thresholds, including 1mm/h, 4mm/h, 8mm/h and 4-8mm/h, as well as a comprehensive decoder covering all rainfall stages. These options can meet the needs of rainfall analysis in different scenarios.You can download these weights at the following address:https://drive.google.com/drive/folders/13FmlCyoBooktR2FNr_MXl71vr86lWbyw?usp=drive_link
```
net.load_state_dict(torch.load("pre.pth"),state_dict=False) 
```
At the same time, we also provide the corresponding diffusion prediction weights,please note that your forecast image is rainfall rather than grayscale or reflectivity.In order to demonstrate the performance of the multi-task decoder, we still use the diffusion model proposed by SSLDM-ISI



