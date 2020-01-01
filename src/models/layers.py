import torch
from torch import nn
from torch.nn import functional as F
from .function import conv2d, deconv2d, batch_norm, lrelu, dropout

'''
TODO : 
1. How to deal with difference size of kinds of input
2. Make a FC module
3. How to apply to CNN Layers
4. Search Another models
5. Consider Our structures
'''
class Encoder_base(nn.Module):
    def __init__(self, 
                 input_category_size=5, input_alpha_size=52, input_font_size=128*128,
                 z_size=64):
        super(Encoder_base, self).__init__()
        input_size = input_category_size + input_alpha_size + input_font_size
        
        self.efc1 = nn.Linear(input_size, 8192)
        self.efc2 = nn.Linear(8192, 128)
        # self.efc3 = nn.Linear(4096, 2048)
        # self.efc4 = nn.Linear(2048, 1024)
        # self.efc5 = nn.Linear(1024, 256)
        # self.efc6 = nn.Linear(256, 128)
        self.efc7 = nn.Linear(128, z_size)
    
    def forward(self, x):
        x = x.view(x.shape[0], -1)
        x = F.relu(self.efc1(x))
        x = F.relu(self.efc2(x))
        # x = F.relu(self.efc3(x))
        # x = F.relu(self.efc4(x))
        # x = F.relu(self.efc5(x))
        # x = F.relu(self.efc6(x))
        z = self.efc7(x)
        return z
    
class Decoder_base(nn.Module):
    def __init__(self, z_latent_size, z_category_size, z_alpha_size, output_font_size=128*128):
        super(Decoder_base, self).__init__()
        
        z_size = z_latent_size + z_category_size + z_alpha_size
        self.dfc1 = nn.Linear(z_size, 128)
        self.dfc2 = nn.Linear(128, 8192)
        # self.dfc3 = nn.Linear(256, 1024)
        # self.dfc4 = nn.Linear(1024, 2048)
        # self.dfc5 = nn.Linear(2048, 4096)
        # self.dfc6 = nn.Linear(4096, 8192)
        self.dfc7 = nn.Linear(8192, output_font_size)
        
    def forward(self, z):
        
        z = F.relu(self.dfc1(z))
        z = F.relu(self.dfc2(z))
        # z = F.relu(self.dfc3(z))
        # z = F.relu(self.dfc4(z))
        # z = F.relu(self.dfc5(z))
        # z = F.relu(self.dfc6(z))
        x_hat = self.dfc7(z)
        return x_hat


class Encoder_conv(nn.Module):

    def __init__(self, img_dim=1, conv_dim=64):
        super(Encoder_conv, self).__init__()
        self.conv1 = conv2d(img_dim, conv_dim, k_size=5, stride=2, pad=2, dilation=2, lrelu=False, bn=False)
        self.conv2 = conv2d(conv_dim, conv_dim * 2, k_size=5, stride=4, pad=2, dilation=2)
        self.conv3 = conv2d(conv_dim * 2, conv_dim * 4, k_size=4, stride=4, pad=1, dilation=1)
        self.conv4 = conv2d(conv_dim * 4, conv_dim * 8)
        self.conv5 = conv2d(conv_dim * 8, conv_dim * 8)

    def forward(self, images):
        images = images.unsqueeze(dim=1)
        e1 = self.conv1(images)
        e2 = self.conv2(e1)
        e3 = self.conv3(e2)
        e4 = self.conv4(e3)
        encoded_source = self.conv5(e4)

        return encoded_source


class Decoder_conv(nn.Module):

    def __init__(self, img_dim=1, embedded_dim=640, conv_dim=64):
        super(Decoder_conv, self).__init__()
        self.deconv1 = deconv2d(embedded_dim, conv_dim * 8, k_size=4, dilation=2, stride=2)
        self.deconv2 = deconv2d(conv_dim * 8, conv_dim * 4, k_size=4, dilation=2, stride=2)
        self.deconv3 = deconv2d(conv_dim * 4, conv_dim * 2, k_size=6, dilation=2, stride=4)
        self.deconv4 = deconv2d(conv_dim * 2, conv_dim * 1, k_size=6, dilation=2, stride=4)
        self.deconv5 = deconv2d(conv_dim * 1, img_dim, k_size=4, dilation=2, stride=2, bn=False)

    def forward(self, embedded):
        d1 = self.deconv1(embedded)
        #print(d1.shape)
        d2 = self.deconv2(d1)
        #print(d2.shape)
        d3 = self.deconv3(d2)
        #print(d3.shape)
        d4 = self.deconv4(d3)
        #print(d4.shape)
        d5 = self.deconv5(d4)
        #print(d5.shape)
        fake_target = d5
        fake_target = fake_target.squeeze(dim=1)

        return fake_target


class Encoder_category(nn.Module):
    def __init__(self,
                 input_font_size=128 * 128,
                 z_size=2):
        super(Encoder_category, self).__init__()
        input_size = input_font_size

        self.efc1 = nn.Linear(input_size, 8192)
        self.efc2 = nn.Linear(8192, 2048)
        self.efc3 = nn.Linear(2048, 1024)
        self.efc4 = nn.Linear(1024, 256)
        self.efc5 = nn.Linear(256, z_size)

    def forward(self, x):
        x = x.view(x.shape[0], -1)
        x = F.relu(self.efc1(x))
        x = F.relu(self.efc2(x))
        x = F.relu(self.efc3(x))
        x = F.relu(self.efc4(x))
        z = self.efc5(x)
        return z


class Decoder_category(nn.Module):
    def __init__(self, z_latent_size, output_font_size=128 * 128):
        super(Decoder_category, self).__init__()

        z_size = z_latent_size
        self.dfc1 = nn.Linear(z_size, 256)
        self.dfc2 = nn.Linear(256, 1024)
        self.dfc3 = nn.Linear(1024, 2048)
        self.dfc4 = nn.Linear(2048, 8192)
        self.dfc5 = nn.Linear(8192, output_font_size)

    def forward(self, z):
        z = F.relu(self.dfc1(z))
        z = F.relu(self.dfc2(z))
        z = F.relu(self.dfc3(z))
        z = F.relu(self.dfc4(z))
        x_hat = self.dfc5(z)
        return x_hat