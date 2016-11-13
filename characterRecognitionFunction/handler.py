#_*_coding: utf-8

from preprocess import preprocess
from characterRecognition import recognizeCharacter
from postprocess import postprocess
from trainTransaction import makeTraineddata 

def recognize(filename, userID, traineddata):
    if preprocess(filename, userID, traineddata) == 0:
        filename = userID + str(traineddata) + '.o2oEditor.exp0.tif'
        if recognizeCharacter(filename, userID, traineddata) == 0:
            filname = userID + str(traineddata) + '.txt'
            postprocess(filename)
            filename = userID + str(traineddata) + '.md'
            # 성공. client에게 .md 전달
            return 0
    # 실패 시 어떠한 행동을 취해야 할지
    return -1

def train(filename, userID, traineddata):
    if preprocess(filename, userID, traineddata) == 0:
        filename = userID + str(traineddata) + '.o2oEditor.exp0.tif'
        if makeTraineddata(filename, userID, traineddata) == 0:
            # train 성공!
            return 0
    # train 실패
    return -1

if __name__ == '__main__':
    #print recognize('image.jpg', 'hwang1', 0)
    print train('131.o2oEditor.exp0.tif', 'hwang', 0)
