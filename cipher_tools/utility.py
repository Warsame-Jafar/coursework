EN_FREQ = [
    0.08167,0.01492,0.02782,0.04253,0.12702,0.02228,0.02015,0.06094,0.06966,
    0.00153,0.00772,0.04025,0.02406,0.06749,0.07507,0.01929,0.00095,0.05987,
    0.06327,0.09056,0.02758,0.00978,0.02360,0.00150,0.01974,0.00074
]
alphabet=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
          'q','r','s','t','u','v','w','x','y','z']



def chi_square(text):
    O=[]
    E=[]
    for i,letter in enumerate(alphabet):

        O.append(text.count(letter))
        E.append(EN_FREQ[i]*len(text))
    cs=0
    for i in range(26):
        cur_O=O[i]
        cur_E=E[i]
        cs+=((cur_O-cur_E)**2)/cur_E
    return cs



def depunctuate(text):
    depunctuated_text=''
    for char in text:
        if char.isalpha():
            depunctuated_text+=char
    return depunctuated_text.lower()
