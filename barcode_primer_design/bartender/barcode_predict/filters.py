import math
import random
import re
from multiprocessing import Pool
from logging import getLogger

from Bio import pairwise2
from Bio.Seq import Seq


log = getLogger(__name__)


def calculate_alignment(sequences, i):
    log.info("seq %s", i)
    seq1 = sequences[i]
    scores = [0] * len(sequences)
    max_penalty = (len(sequences) * len(sequences)) / 2 - len(sequences)
    for j, seq2 in enumerate(sequences):
        if j <= i:
            continue
        score = pairwise2.align.globalxx(seq1, seq2)[0][2]
        score_revcomp = pairwise2.align.globalxx(
            str(Seq(seq1).reverse_complement()), seq2
        )[0][2]
        max_score = max(score, score_revcomp)
        if max_score < 7:
            scores[j] = 7 - max_score
        else:
            scores[j] = -1 * max_penalty
    return scores


def f(m, v):
    s = 0
    for i in range(len(v)):
        for j in range(i + 1, len(v)):
            s = s + m[v[i]][v[j]]
    return s


def evaluate(cur_score, new_score, t):
    if new_score >= cur_score:
        return True
    elif t > 0 and math.exp((-(cur_score - new_score)) / t) > random.uniform(0, 1):
        return True
    else:
        return False


def simulated_annealing(m):
    v = random.sample(range(len(m)), 100)
    cur_score = f(m, v)
    scores = []
    cooling_iterations = 300
    t = 10000.0
    decr = t / cooling_iterations
    no_change = 0
    i = 0

    while no_change < 500:
        if t > decr:
            t -= decr
        else:
            t = 0

        p = random.uniform(0, 1)
        scores.append(cur_score)
        it_score = cur_score

        j = random.randint(0, len(v) - 1)
        if p <= 0.1:
            v_new = list(v)
            v_new.pop(j)
            if len(v) > 2:
                new_score = f(m, v_new)
                if evaluate(cur_score, new_score, t):
                    v = v_new
                    cur_score = new_score
        else:
            indices = [x for x in range(len(m)) if x not in v]
            random.shuffle(indices)
            for k in indices:
                v_new = list(v)

                if p > 0.4:
                    v_new[j] = k
                else:
                    v_new.append(k)

                new_score = f(m, v_new)
                if evaluate(cur_score, new_score, t):
                    v = v_new
                    cur_score = new_score

        if cur_score > it_score:
            log.info(
                "no change: %s, it score: %s, cur score: %s, t: %s",
                no_change,
                it_score,
                cur_score,
                t,
            )
            no_change = 0

        else:
            no_change += 1

        i += 1

    outfile = open("scores_new.txt", "w")
    for score in scores:
        outfile.write(str(score) + "\n")
    outfile.close()

    return v


def gc_content(sequences, num_gc):
    return [
        act_seq
        for act_seq in sequences
        if len(re.findall(r"[cg]", act_seq, flags=re.IGNORECASE)) == num_gc
    ]


def repeats(sequences, num_repeats, length_repeats):
    new_sequences = []

    for seq in sequences:
        has_repeat = False
        for l in range(length_repeats):
            m = re.search(
                rf"(([gatc]{{{l+1}}})\2{{{num_repeats}}})", seq, flags=re.IGNORECASE
            )
            if m is not None:
                has_repeat = True
        if has_repeat is not True:
            new_sequences.append(seq)

    return new_sequences


def similarity(sequences):
    sequences = random.sample(sequences, 1000)
    score_matrix = []

    pool = Pool(processes=5)
    results = []
    for i, seq1 in enumerate(sequences):
        results.append(pool.apply_async(calculate_alignment, args=(sequences, i)))

    pool.close()
    pool.join()

    for res in results:
        score_matrix.append(res.get())

    for i in range(len(score_matrix)):
        for j in range(i + 1, len(score_matrix)):
            score_matrix[j][i] = score_matrix[i][j]

    with open("score_matrix_new.txt", "w") as best:
        for i in range(0, len(sequences)):
            best.write(sequences[i] + "\t")
        best.write("\n")
        for i in range(0, len(sequences)):
            best.write(sequences[i] + "\t")
            for j in range(0, len(sequences)):
                best.write(str(score_matrix[i][j]) + "\t")
            best.write("\n")

    v = simulated_annealing(score_matrix)

    with open("best_new.txt", "w") as best:
        for i in v:
            best.write(sequences[i] + "\t")
        best.write("\n")
        for i in v:
            best.write(sequences[i] + "\t")
            for j in v:
                ind_i = sorted([i, j])
                best.write(str(score_matrix[ind_i[0]][ind_i[1]]) + "\t")
            best.write("\n")
