#_*_coding: utf-8

# markdownw 적용 안됨

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

    content = list(content)

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

    print content
            
    f = open(filename, 'w')

    f.write(content)

    f.close()

    return 0

heuristic('post.txt')
# Ex. l am a bOy. => I am a boy.
