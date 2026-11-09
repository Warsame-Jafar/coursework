
import math
import random
import re
import time
from collections import Counter

alphabet = list("abcdefghijklmnopqrstuvwxyz")


#applies a substitution mapping while preserving case and punctuation
def apply_substitution(text, key_cipher_to_plain):
    out = []
    for ch in text:
        if ch.isalpha():
            up = ch.upper()
            mapped = key_cipher_to_plain.get(up, up)
            out.append(mapped.lower() if ch.islower() else mapped)
        else:
            out.append(ch)
    return "".join(out)


#builds n gram log probabilities from an english corpus
def _ngram_logprobs_dense(corpus, n, k=0.5):
    AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    A2I = {c: i for i, c in enumerate(AZ)}
    t = re.sub(r"[^A-Z]", "", corpus.upper())

    counts = Counter()
    for i in range(len(t) - n + 1):
        idx = 0
        for j in range(n):
            idx = idx * 26 + A2I[t[i + j]]
        counts[idx] += 1

    total = sum(counts.values())
    vocab = 26 ** n
    denom = total + k * vocab
    floor = math.log(k / denom)
    arr = [floor] * vocab

    for idx, c in counts.items():
        arr[idx] = math.log((c + k) / denom)

    return arr, floor


#creates a starting key using english letter frequency order
def _freq_start_key(text, AZ):
    EN = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
    t = re.sub(r"[^A-Z]", "", text.upper())
    cnt = Counter(t)
    order = [p[0] for p in cnt.most_common()]

    for a in AZ:
        if a not in order:
            order.append(a)

    return {order[i]: EN[i] for i in range(26)}


DEFAULT_CORPUS = """
IN THE BEGINNING GOD CREATED THE HEAVEN AND THE EARTH AND THE EARTH WAS WITHOUT FORM AND VOID
AND DARKNESS WAS UPON THE FACE OF THE DEEP AND THE SPIRIT MOVED UPON THE FACE OF THE WATERS
WE HOLD THESE TRUTHS TO BE SELF EVIDENT THAT ALL MEN ARE CREATED EQUAL AND ENDOWED WITH CERTAIN
UNALIENABLE RIGHTS AMONG THESE ARE LIFE LIBERTY AND THE PURSUIT OF HAPPINESS
WHEN YOU HAVE ELIMINATED THE IMPOSSIBLE WHATEVER REMAINS HOWEVER IMPROBABLE MUST BE THE TRUTH
IT WAS THE BEST OF TIMES IT WAS THE WORST OF TIMES IT WAS THE AGE OF WISDOM IT WAS THE AGE OF FOOLISHNESS
CALL ME ISHMAEL SOME YEARS AGO NEVER MIND HOW LONG PRECISELY HAVING LITTLE OR NO MONEY IN MY PURSE
I AM AN INVISIBLE MAN NO I AM NOT A SPOOK LIKE THOSE WHO HAUNT EDGAR ALLAN POE
THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG
"""


#second iteration monoalphabetic substitution breaker
def substitution_break(ciphertext, max_restarts=8, sa_steps=4000, seed=42):
    AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    A2I = {c: i for i, c in enumerate(AZ)}

    CT = ciphertext
    CT_UP = CT.upper()

    #keeps only alphabetic characters for scoring
    L = [A2I[ch] for ch in CT_UP if "A" <= ch <= "Z"]
    nL = len(L)

    #returns safely if there are too few letters
    if nL < 8:
        key = _freq_start_key(CT, AZ)
        return key, apply_substitution(CT, key)

    #builds english scoring models
    lp2, _ = _ngram_logprobs_dense(DEFAULT_CORPUS, 2, k=0.5)
    lp3, _ = _ngram_logprobs_dense(DEFAULT_CORPUS, 3, k=0.5)
    lp4, _ = _ngram_logprobs_dense(DEFAULT_CORPUS, 4, k=0.5)

    #converts a dictionary key into a permutation list
    def freq_start_key_list():
        d = _freq_start_key(CT, AZ)
        arr = [0] * 26
        for c_ch, p_ch in d.items():
            arr[A2I[c_ch]] = A2I[p_ch]
        return arr

    #creates a random substitution key
    def random_key_list(rng):
        arr = list(range(26))
        rng.shuffle(arr)
        return arr

    #scores a candidate key using english n grams
    def full_score(P):
        s = 0.0

        if nL >= 4:
            for i in range(nL - 3):
                a, b, c, d = P[L[i]], P[L[i + 1]], P[L[i + 2]], P[L[i + 3]]
                s += lp4[((a * 26 + b) * 26 + c) * 26 + d]

        if nL >= 3:
            for i in range(nL - 2):
                a, b, c = P[L[i]], P[L[i + 1]], P[L[i + 2]]
                s += lp3[(a * 26 + b) * 26 + c]

        if nL >= 2:
            for i in range(nL - 1):
                a, b = P[L[i]], P[L[i + 1]]
                s += lp2[a * 26 + b]

        return s

    #runs one simulated annealing restart
    def one_restart(rng, use_freq_start):
        if use_freq_start:
            P = freq_start_key_list()
        else:
            P = random_key_list(rng)

        current_score = full_score(P)
        best_score = current_score
        best_P = P[:]

        start_temp = 8.0
        end_temp = 0.2

        for step in range(1, sa_steps + 1):
            temp = start_temp * ((end_temp / start_temp) ** (step / sa_steps))

            a = rng.randrange(26)
            b = rng.randrange(26)
            if a == b:
                continue

            test = P[:]
            test[a], test[b] = test[b], test[a]
            score = full_score(test)
            delta = score - current_score

            #accepts better swaps and occasionally worse ones
            if delta > 0 or rng.random() < math.exp(delta / max(temp, 1e-12)):
                P = test
                current_score = score

                if current_score > best_score:
                    best_score = current_score
                    best_P = P[:]

        return best_P, best_score

    best_overall_score = float("-inf")
    best_overall_key = None

    #uses multiple restarts so the solver is less dependent on one start point
    for restart in range(max_restarts):
        rng = random.Random(seed + restart)

        if restart == 0:
            P, score = one_restart(rng, True)
        else:
            P, score = one_restart(rng, False)

        if score > best_overall_score:
            best_overall_score = score
            best_overall_key = P[:]

    #converts the final permutation back into a cipher to plain dictionary
    key_cipher_to_plain = {AZ[c]: AZ[best_overall_key[c]] for c in range(26)}
    plaintext = apply_substitution(CT, key_cipher_to_plain)

    return key_cipher_to_plain, plaintext
print(substitution_break(input()))