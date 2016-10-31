#_*_coding: utf-8

import os
import pytesseract
from PIL import Image
import commands

path = 'C:\Users\USER1\Desktop\O2O\src\mid' 
filename = 'train.test.exp0'
lang = filename.split('.')[0]
fontname = filename.split('.')[1]
num = filename.split('.')[2]


os.system('cd %s'%path)

os.system('tesseract %s.tif %s -l eng batch.nochop makebox'%(filename,filename))
f = open('C:\Users\USER1\Desktop\O2O\src\mid\\train.test.exp0.box','r')
print '1'
myString = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"

myBox = []

for char in myString:
    string = f.readline()
    print string
    string = list(string)
    string[0] = char
    string = "".join(string)
    myBox.append(string)

f.close()

f = open('C:\Users\USER1\Desktop\O2O\src\mid\\train.test.exp0.box','w')

for string in myBox:
    f.write(string)

f.close()


f = open('C:\Users\USER1\Desktop\O2O\src\mid\\train.test.exp0.box','r')

print f.read()
f.close()
print '4'
os.system('tesseract %s.tif %s nobatch box.train'%(filename, filename))

os.system('unicharset_extractor %s.box'%filename)

f = open('C:\Users\USER1\Desktop\O2O\src\mid'+'/font_properties','a')
f.write("%s 0 0 0 0 0"%fontname)
f.close()
print '2'
os.system('shapeclustering -F font_properties -U unicharset %s.tr'%filename)
os.system('mftraining -F font_properties -U unicharset -O %s.unicharset %s.tr'%(lang,filename))
os.system('cntraining %s.tr'%filename)

os.system('move inttemp %s.inttemp'%lang)
os.system('move normproto %s.normproto'%lang)
os.system('move pffmtable %s.pffmtable'%lang)
os.system('move shapetable %s.shapetable'%lang)
os.system('combine_tessdata %s.'%lang)
###########os.system('mv C:\

print '3'

os.system('tesseract %s.tif %s -l %s'%(fontname, fontname, lang))
fail, output = commands.getstatusoutput("tesseract myeng.test.exp0.tif test -l myeng")
#print(pytesseract.image_to_string(Image.open("C:\Python27\haha\\myeng.test.exp0.tif")))
