from utility import depunctuate, alphabet, chi_square


def vigenere_break(message):
    message=depunctuate(message)
    most_ngram_occurences=0
    most_common_ngram=''
    ngram_length=4
    for i,letter in enumerate(message):
        if i+ngram_length<len(message):
            current_ngram=message[i:i+ngram_length]
            no_of_occurences=message.count(current_ngram)
        if no_of_occurences > most_ngram_occurences:
            most_ngram_occurences= no_of_occurences
            most_common_ngram= current_ngram
    # finds most common n-gram and the number of times it occurs
    original_message=message
    gaps=[]
    split=False
    for i in range(most_ngram_occurences):
        ngram_index=message.find(most_common_ngram)+ngram_length
        message = message[ngram_index:]
        if split:
            gaps.append(ngram_index)
        split=True
    gaps.sort()
    # finds the length of gaps between occurences of most common n-gram
    possible_lengths=[]
    for i in range(1,gaps[0]):
        common_factor=True
        for num in gaps:
            if num%i!=0:
                common_factor=False
        if common_factor:
            possible_lengths.append(i)
    # finds all common factors of gaps between n-grams and stores as possible key lengths
    message=original_message
    possible_keys=[]
    for length in possible_lengths: # goes through each possible key length
        current_key_score=0
        current_key=''
        # testing each possible key length
        columns=['' for i in range(length)] # creating a list to separate text into columns based on key length

        for i,letter in enumerate(message):
            columns[i%length]+=letter # arranging text into columns
        
        for i,column in enumerate(columns): # goes through each column

            shift_scores=[]
            for shift in range(26):
                shifted=''
                for letter in column:
                    shifted+=alphabet[(alphabet.index(letter)-shift)%26]
                if i==1 and shift==3 and length==3:
                    print(column)
                    print(shifted)
                shift_scores.append((shift,chi_square(shifted))) # testing caesar shift on each column and evaluating based on chi-square score
                    
                    
            shift_scores.sort(key= lambda x: abs(0-x[1])) # sorting possible shifts in order of chi-square score 
            
            current_key+=alphabet[shift_scores[0][0]] # adding best letter for current column to key
            current_key_score+=shift_scores[0][1]
        possible_keys.append((current_key,current_key_score))
        possible_keys.sort(key=lambda x:x[1])
    best_key=possible_keys[0][0]
    best_plaintext=''
    for i,letter in enumerate(message):
        shift=alphabet.index(best_key[i%len(best_key)])
        best_plaintext+=alphabet[(alphabet.index(letter)-shift)%26] # decoding ciphertext based on best key
    
    return best_key, best_plaintext


                
                    


    

    
key,plaintext=vigenere_break(input('enter message: '))
print(f'key: {key}')
print(f'plaintext: {plaintext}')
        
        
