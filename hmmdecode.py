import sys
import json
import math
from collections import defaultdict
from collections import Counter


def read_model(model_file):
    trans_prob = defaultdict(lambda: defaultdict(float))
    emmis_prob = defaultdict(lambda: defaultdict(float))
    with open(model_file, "r", encoding="utf-8") as mfile:
        model = mfile.readlines()
    for lines in model:

        data = lines.split()
        tag = data[0]
        word_or_tag = data[1]
        rest = data[2:]
        for items in rest:

            elem, probability = items.rsplit("=", 1)
            if word_or_tag == "->Tag":
                trans_prob[tag][elem] = float(probability)
            elif word_or_tag == "->Word":
                emmis_prob[tag][elem] = float(probability)

    return trans_prob, emmis_prob


def get_tokens(dev_file):
    file = open(dev_file, "r", encoding="utf-8")
    f = file.readlines()
    all_tokens_sequences = []
    for lines in f:
        tokens = lines.split()
        all_tokens_sequences.append(tokens)
    return all_tokens_sequences


def viterbi_decoding(transition_prob, emission_prob, test_tokens_sequences):
    all_tags = list(transition_prob.keys())
    all_tags.remove("$#@rt")
    output_str = ""
    unseen = set()
    all_words = set()

    for tag in emission_prob.keys():
        for word in emission_prob[tag]:
            all_words.add(word)

    for sequence in test_tokens_sequences:
        max_probabilities = {}
        back_pointers = {}
        max_probabilities[0] = dict.fromkeys(all_tags, 0)

        for current_tag in all_tags:
            if sequence[0] in emission_prob[current_tag]:
                max_probabilities[0][current_tag] = math.log(transition_prob["$#@rt"][current_tag]) + math.log(
                    emission_prob[current_tag][sequence[0]])

            elif sequence[0] not in all_words:
                # if word is a digit then give tag N
                if sequence[0][0].isdigit():
                    if current_tag == "N":
                        max_probabilities[0][current_tag] = math.log(transition_prob["$#@rt"][current_tag])
                    else:
                        max_probabilities[0][current_tag] = math.log(transition_prob["$#@rt"][current_tag]) - 9000
                # if current tag is open tag
                elif len(emission_prob[current_tag].keys()) > 1000:
                    max_probabilities[0][current_tag] = math.log(transition_prob["$#@rt"][current_tag])
                # if current tag is closed tag
                else:
                    max_probabilities[0][current_tag] = math.log(transition_prob["$#@rt"][current_tag]) - 9000
            else:
                max_probabilities[0][current_tag] = math.log(transition_prob["$#@rt"][current_tag]) - 9000

        for i in range(1, len(sequence)):
            max_probabilities[i] = dict.fromkeys(all_tags, 0)
            back_pointers[i] = dict.fromkeys(all_tags, "")
            for current_tag in all_tags:
                max_prob = float("-inf")
                for prev_tag in max_probabilities[i - 1]:

                    if sequence[i] in emission_prob[current_tag]:
                        temp = math.log(transition_prob[prev_tag][current_tag]) + math.log(
                            emission_prob[current_tag][sequence[i]]) + max_probabilities[i - 1][prev_tag]
                    elif sequence[i] not in all_words:
                        # if word is a digit then give tag N
                        if sequence[i][0].isdigit():
                            if current_tag == "N":
                                temp = math.log(transition_prob[prev_tag][current_tag]) + max_probabilities[i - 1][
                                    prev_tag]
                            else:
                                temp = math.log(transition_prob[prev_tag][current_tag]) + max_probabilities[i - 1][
                                    prev_tag] - 9000
                        # if current tag is open tag
                        elif len(emission_prob[current_tag].keys()) > 1000:
                            temp = math.log(transition_prob[prev_tag][current_tag]) + max_probabilities[i - 1][prev_tag]
                        # if current tag is closed tag
                        else:
                            temp = math.log(transition_prob[prev_tag][current_tag]) + max_probabilities[i - 1][
                                prev_tag] - 9000
                    else:

                        temp = math.log(transition_prob[prev_tag][current_tag]) + max_probabilities[i - 1][
                            prev_tag] - 9000

                    if temp > max_prob:
                        max_prob = temp
                        max_probabilities[i][current_tag] = temp
                        back_pointers[i][current_tag] = prev_tag
        # add end state probabilities
        final_max_prob = float("-inf")
        for tag in max_probabilities[len(sequence) - 1].keys():
            if max_probabilities[len(sequence) - 1][tag] + transition_prob[tag]["*@END"] > final_max_prob:
                final_max_prob = max_probabilities[len(sequence) - 1][tag] + transition_prob[tag]["*@END"]
                final_tag = tag

        predicted_tags = [final_tag]
        ans_tag = final_tag

        # backtrack
        for j in range(len(sequence) - 1, 0, -1):
            ans_tag = back_pointers[j][ans_tag]
            predicted_tags.append(ans_tag)

        predicted_tags.reverse()

        for i, word in enumerate(sequence):
            output_str += str(word) + "/" + str(predicted_tags[i]) + " "
        output_str = output_str[:-1]
        output_str += "\n"

    with open("hmmoutput.txt", "w", encoding="utf-8") as output_file:
        output_file.write(output_str)

def main():
    model_file = "hmmmodel.txt"
    dev_file = sys.argv[1]
    transition_prob, emission_prob = read_model(model_file)
    test_tokens_sequences = get_tokens(dev_file)
    viterbi_decoding(transition_prob, emission_prob, test_tokens_sequences)

if __name__ == "__main__":
    ignore_files_pattern = r"(README|DS_Store|LICENSE)"
    main()