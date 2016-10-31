#_*_coding: utf-8

from PIL import Image
import scipy.misc
import matlab.engine

# preprocessing
def preprocessing(filename):
    eng = matlab.engine.start_matlab()
    I = eng.imread(filename)

    level = eng.graythresh(I)
    BW = eng.im2bw(I,level*1.1)

    BW2 = eng.bwareaopen(BW,float(12))
    img = eng.im2single(BW2)

    #eng.workspace['hopening'] = eng.vision.MorphologicalOpen
    #eng.workspace['hopening.Neighborhood'] = eng.strel('disk', float(2))
    #img = eng.step(eng.workspace['hopening'], img)

    filename = filename.split('.')

    fullfilename = eng.fullfile('C:\Users\USER1\Desktop\O2O\src\mid','.'.join(filename[:-1]) + '.tif')
    scipy.misc.imsave(fullfilename, img)

    eng.quit

preprocessing('train.test.exp0.jpg')
