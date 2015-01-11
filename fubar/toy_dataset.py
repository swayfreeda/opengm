import numpy
import opengm
from opengm import learning
import vigra
from progressbar import *
import glob
import os
from functools import partial
from make_grid_potts_dset import secondOrderImageDataset, getPbar



nImages = 8 
shape = [100, 100]
noise = 3
imgs = []
gts = []


for i in range(nImages):

    gtImg = numpy.zeros(shape)
    gtImg[0:shape[0]/2,:] = 1

    gtImg[shape[0]/4: 3*shape[0]/4, shape[0]/4: 3*shape[0]/4]  = 2

    ra = numpy.random.randint(180)
    #print ra 

    gtImg = vigra.sampling.rotateImageDegree(gtImg.astype(numpy.float32),int(ra),splineOrder=0)

    if i==0 :
        vigra.imshow(gtImg)
        vigra.show()

    img = gtImg + numpy.random.random(shape)*float(noise)
    if i==0:
        vigra.imshow(img)
        vigra.show()

    imgs.append(img.astype('float32'))
    gts.append(gtImg)







def getSelf(img):
    return img


def getSpecial(img, sigma):
    simg = vigra.filters.gaussianSmoothing(img, sigma=sigma)

    img0  = simg**2
    img1  = (simg - 1.0)**2
    img2  = (simg - 2.0)**2

    img0=img0[:,:,None]
    img1=img1[:,:,None]
    img2=img2[:,:,None]

    img3 = numpy.exp(-1.0*img0)
    img4 = numpy.exp(-1.0*img1)
    img5 = numpy.exp(-1.0*img2)
    return numpy.concatenate([img0,img1,img2,img3,img4,img5],axis=2)


fUnary = [
    partial(getSpecial, sigma=0.5),
    partial(getSpecial, sigma=1.0),
    partial(getSpecial, sigma=1.5),
    partial(getSpecial, sigma=2.0),
    partial(getSpecial, sigma=3.0),
]

fBinary = [
    partial(vigra.filters.gaussianGradientMagnitude, sigma=0.5),
    partial(vigra.filters.gaussianGradientMagnitude, sigma=1.0),
    partial(vigra.filters.gaussianGradientMagnitude, sigma=1.5),
    partial(vigra.filters.gaussianGradientMagnitude, sigma=2.0),
    partial(vigra.filters.gaussianGradientMagnitude, sigma=3.0),
]


dataset,test_set = secondOrderImageDataset(imgs=imgs, gts=gts, numberOfLabels=3, 
                                          fUnary=fUnary, fBinary=fBinary, 
                                          addConstFeature=False)






learner =  learning.subgradientSSVM(dataset, learningRate=10.5, C=100, learningMode='batch',maxIterations=500,averaging=2)

learningModi = ['normal','reducedinference','selfFusion','reducedinferenceSelfFusion']
lm = 0


infCls = opengm.inference.TrwsExternal
param = opengm.InfParam()


#with opengm.Timer("n  2"):
#    learner.learn(infCls=infCls,parameter=param,connectedComponents=True,infMode='n')
#with opengm.Timer("sf"):
#    learner.learn(infCls=infCls,parameter=param,connectedComponents=True,infMode='sf')
with opengm.Timer("ri"):
    learner.learn(infCls=infCls,parameter=param,connectedComponents=True,infMode='ri')
#with opengm.Timer("risf"):
#    learner.learn(infCls=infCls,parameter=param,connectedComponents=True,infMode='risf')



# predict on test test
for (rgbImg, gtImg, gm) in test_set :
    # infer for test image
    inf = opengm.inference.TrwsExternal(gm)
    inf.infer()
    arg = inf.arg()
    arg = arg.reshape( numpy.squeeze(gtImg.shape))

    vigra.imshow(arg+2)
    vigra.show()

