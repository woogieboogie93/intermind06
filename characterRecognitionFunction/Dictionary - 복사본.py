#_*_coding: utf-8

import string
import dictionary
import sqlite3

def replaceWord(filename):

    f = open(filename)

    origin = f.read()
    print origin
    text = origin
    

    punc = list(string.punctuation+string.whitespace) 
    print punc
    for i in punc:
        print type(i)
        text = text.replace(i,' ')
    print text

    words = [word for word in text.split(' ') if len(text)>1 ]
    print words

    # dic
    dic = dictionary.Dictionary()
    
    # db
    conn = sqlite3.connect('wordFrequency.db')
    
    c = conn.cursor()
    try:
        c.execute('''create table words (word text, frequency real)''')
    except: pass

    # for문을 돌면서 같은거 못찾으면 바꿔주는 식?????
    for word in words:
        print word
        print 'C'
        if not dic.isInDictionary(word) and len(word) > 1: # dic에 없으면
            print 'D'
            try:
                print 'uuuuu'
                similarWord = dic.getSimilarWords(word) # ????????
                #print similarWords
                print 'yyyyyyyuy'
                #wordFrequency = [] # (단어,횟수)를 저장
                
                print 'hwang'
                #c.execute('select * from words where word = ?', (similarWord,))
                #frequency = c.fetchone()
                print B
                #if frequency != None:
                #    wordFrequency.append(frequency)
                #sorted(wordFrequency, key = lambda x: x[1])
                origin.replace(word, similarWord)
                #word = wordFrequency[0][0] # 존재하는 경우는 +1
                #c.execute('update words set frequency = ? where word = ?',(wordFrequency[0][1]+1, wordFrequency[0][0]))
                #words.remove(word) # ????
                print 'A'
            except: pass # 비슷한것도 못찾음. 사전에 없는 단어임. pass
        #else : words.remove(word) # ????? 추가해줘야해

    #for word in words:
        #c.execute('insert into words values (?,?)', (word, 1))

    conn.commit()
    conn.close()

    print 'last  :',origin
    f = open(filename,'w')
    f.write(origin)
    f.close()
    
    return 0


if __name__ == '__main__':
    print replaceWord('newhaha3.txt')
