#_*_coding: utf-8

import string
import dictionary
import sqlite3

# markdownw 적용 안됨

def postprocess(filename):
    '''
    if heuristic(filename) == 0:
        filename = filename.split('.')
        filename = '.'.join(filename[:-1]) + '.md'
        return referToDictionary(filename)
    return -1
    '''
    return heuristic(filename)

def heuristic(filename):

    whitespace = ['\t', '\n', '\r', '\f', '\v', ' ']
    lowerToUpper = {'o':'O', 'p':'P', 'l':'I', 'x':'X', 'v':'V', 'z':'Z'}
    upperToLower = {'O':'o', 'P':'p', 'I':'l', 'X':'x', 'V':'v', 'Z':'z'}

    case = [punc + space for punc in ['.', '!', '?'] for space in whitespace]

    try:
        f = open(filename, 'r')
    except:
        return -1
    content = f.read()
    f.close()

    if content == '':
        return -1
    content = list(content)
    #print content

    if content[0] in lowerToUpper.keys():
        content[0] = lowerToUpper[content[0]]

    if content[1] in lowerToUpper.keys():
        if content[0] in whitespace:
            content[1] = lowerToUpper[content[1]]
    if content[1] in upperToLower.keys():
        if content[0] not in whitespace:
            content[1] = upperToLower[content[1]]

    for i in range(2, len(content)):
        if content[i] in lowerToUpper.keys():
            if content[i - 2] + content[i - 1] in case:
                content[i] = lowerToUpper[content[i]]
        if content[i] in upperToLower.keys():
            if content[i - 2] + content[i - 1] not in case:
                content[i] = upperToLower[content[i]]

    content = ''.join(content)

    filename = filename.split('.')
    filename = '.'.join(filename[:-1]) + '.md'
    #print filename
            
    f = open(filename, 'w')

    f.write(content)

    f.close()

    #print 'heuristic end'
    return 0

# 
def referToDictionary(filename):

    try:
        f = open(filename)
    except:
        return -1

    try:
        origin = '\n'.join([unicode(line, errors = 'ignore') for line in f.readlines()])
        f.close()
    except:
        return -1
    words = origin

    punc = list(string.punctuation+string.whitespace) 
    for i in punc:
        words = words.replace(i,' ')

    newWords = [word for word in words.split(' ') if len(word) > 1 ]
    words = [word for word in words.split(' ') if len(word) > 1 ]
    

    dic = dictionary.Dictionary()    
    conn = sqlite3.connect('wordFrequency.db')
    c = conn.cursor()
    #print 'start'
    try:
        c.execute('''create table words (word text, frequency real)''')
    except: pass

    #print 'words'
    #print words
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

    print 'dictionary end'
    
    return 0


if __name__ == '__main__':
    postprocess('h0.txt')
    
# Ex. l am a bOy. => I am a boy.
