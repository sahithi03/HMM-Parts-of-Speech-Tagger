import sys
from collections import defaultdict
import json

# Add one smoothing
def perform_add_one_smoothing(transition_prob, all_tags):
    second_state_tags = list(all_tags) + ["*@END"]
    for old_tag in all_tags:
        for new_tag in second_state_tags:
            if new_tag not in transition_prob[old_tag]:
                transition_prob[old_tag][new_tag] = 1
            else:
                transition_prob[old_tag][new_tag] += 1

    return transition_prob

# Transition Probability
def get_transition_probability(transition_prob, all_tags):
    second_state_tags = list(all_tags) + ["*@END"]
    for old_tag in all_tags:
        total_val = sum(transition_prob[old_tag].values())
        for new_tag in second_state_tags:
            transition_prob[old_tag][new_tag] = transition_prob[old_tag][new_tag] / total_val
    return transition_prob

# Emission Probability
def get_emission_probability(emission_prob):
    for tag in emission_prob.keys():
        total_val = sum(emission_prob[tag].values())

        for word in emission_prob[tag]:
            emission_prob[tag][word] = emission_prob[tag][word] / total_val
    return emission_prob

def main():
    training_file = sys.argv[1]

    with open(training_file) as file:
        train_data = file.readlines()
    transition_prob = defaultdict(lambda: defaultdict(int))
    emission_prob = defaultdict(lambda: defaultdict(int))
    all_tags = set()
    for line in train_data:
        token_sequence = line.split()
        prev_tag = "$#@rt"
        all_tags.add(prev_tag)
        for i, token in enumerate(token_sequence):
            word, tag = token.rsplit("/", 1)
            transition_prob[prev_tag][tag] += 1
            emission_prob[tag][word] += 1
            all_tags.add(tag)
            prev_tag = tag
        # add end state
        transition_prob[prev_tag]["*@END"] += 1

    new_transition_counts = perform_add_one_smoothing(transition_prob, all_tags)
    transition_prob = get_transition_probability(new_transition_counts, all_tags)
    emission_prob = get_emission_probability(emission_prob)

    output_file = open("hmmmodel.txt", 'w', encoding='utf-8')
    output_str = ""

    for prev_tag in transition_prob:
        output_str += str(prev_tag) + " " + str("->Tag")
        for new_tag in transition_prob[prev_tag]:
            output_str += " " + str(new_tag) + "=" + str(transition_prob[prev_tag][new_tag]) + " "
        output_str += "\n"

    for tag in emission_prob:
        output_str += str(tag) + " " + str("->Word")
        for word in emission_prob[tag]:
            output_str += " " + str(word) + "=" + str(emission_prob[tag][word]) + " "
        output_str += "\n"
    output_file.write(output_str[:-1])
    output_file.close()


if __name__ == "__main__":
    ignore_files_pattern = r"(README|DS_Store|LICENSE)"
    main()