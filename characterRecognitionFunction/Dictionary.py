#_*_coding: utf-8

import string
import dictionary
import sqlite3

# 파일이 없는 경우 ??
# 일단 안되면 return -1

def replaceWord(filename):

    try:
        f = open(filename)
    except:
        return -1

    origin = '\n'.join([line.decode('utf-8').strip() for line in f.readlines()])
    words = origin

    punc = list(string.punctuation+string.whitespace) 
    for i in punc:
        words = words.replace(i,' ')

    newWords = [word for word in words.split(' ') if len(word) > 1 ]
    words = [word for word in words.split(' ') if len(word) > 1 ]
    

    dic = dictionary.Dictionary()    
    conn = sqlite3.connect('wordFrequency.db')
    c = conn.cursor()
    try:
        c.execute('''create table words (word text, frequency real)''')
    except: pass

    for word in words:
        if not dic.isInDictionary(word) and len(word) > 1:
            try:
                similarWords = dic.getSimilarWords(word)
                wordFrequency = []
                for similarWord in similarWords:
                    c.execute('select * from words where word = ?', (similarWord,))
                    frequency = c.fetchone()
                    if frequency != None:
                        wordFrequency.append(frequency)
                if wordFrequency == []:
                    origin = origin.replace(word, similarWords[0])
                    word = similarWords[0]
                else:
                    sorted(wordFrequency, key = lambda x: x[1])
                    origin = origin.replace(word, wordFrequency[0][0])
                    c.execute('update words set frequency = frequency + 1 where word = ?',(wordFrequency[0][0]))
                    newWords.remove(word)
            except: pass
        else :
            c.execute('select * from words where word = ?', (word,))
            if c.fetchone():
                c.execute('update words set frequency = frequency + 1 where word = ?',(word,))#####
                newWords.remove(word)

    words = newWords

    for word in words:
        c.execute('insert into words values (?,?)', (word, 1))

    conn.commit()
    conn.close()

    f = open(filename,'w')
    f.write(origin.encode('utf8'))
    f.close()
    
    return 0
    
if __name__ == '__main__':
    print replaceWord('ex6.txt')
