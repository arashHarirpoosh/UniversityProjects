import os
import math


# Read The Data From txt File
def read_data(addr):
    f = open(addr, "r", encoding='utf-8')
    return f


# Read The Test Data From txt File And Determine The Inputs And Label Of The Poems
def read_test_data(addr):
    data = read_data(addr)
    all_lines = data.readlines()
    y_labels = ['ferdowsi', 'hafez', 'molavi']
    x = []
    y = []
    for l in all_lines:
        data_part = l.split('\t')
        x.append(data_part[1].replace('\n', ''))
        y.append(y_labels[int(data_part[0]) - 1])
    return x, y


# Calculate The Number Of Times That One Word Repeated In Train DataSet
def histogram_of_words(lines):
    hist = {}
    for l in lines:
        words = l.split(' ')
        for w in words:
            pure_word = w.replace('\n', '')
            if pure_word not in hist.keys():
                hist[pure_word] = 1
            else:
                hist[pure_word] += 1
    return hist


# Remove Words That Are Not Frequent In The DataSet
def eliminate_non_redundant_words(hist, min_count=2):
    redundant_words = {key: val for key, val in hist.items() if val > min_count}
    return redundant_words


# Calculate The Number Of Time's That Two Words Repeated Sequentially After Each Other
# Calculate The Bigram Model
def bigram(lines):
    bigram_count = {}
    for l in lines:
        edited = '<s> ' + l.replace('\n', '') + ' <\s>'
        words = edited.split()
        num_of_line_words = len(words)
        for w in range(1, num_of_line_words):
            prob_name = words[w] + '|' + words[w - 1]
            if prob_name not in bigram_count.keys():
                bigram_count[prob_name] = 1
            else:
                bigram_count[prob_name] += 1
    return bigram_count


# Calculate The Probability's Of Bigram Model
def calculate_bigram_probs(count_bigram, number_of_words, number_of_lines):
    bigram_probs = {}
    for k, v in count_bigram.items():
        previous_word = k.split('|')[1]
        if previous_word == '<s>':
            bigram_probs[k] = math.log2(count_bigram[k] / number_of_lines)
        else:
            bigram_probs[k] = math.log2(count_bigram[k] / number_of_words[previous_word])
    return bigram_probs


# Calculate The Probability's That Needed In The Model According To One Class In The Train DataSet
# Calculate The Unigram And Bigram Model Of One Class In The Train DataSet
def train_model(data):
    word_hist = histogram_of_words(data)
    valid_word_hist = eliminate_non_redundant_words(word_hist)
    word_count = len(valid_word_hist)
    num_of_words = sum(valid_word_hist.values())
    bigram_count = bigram(data)
    bigram_prob = calculate_bigram_probs(bigram_count, word_hist, len(data))
    class_model = {'NumberOfLines': len(valid_word_hist),
                   'Unigram': {key: math.log2(val / num_of_words) for key, val in valid_word_hist.items()},
                   'Bigram': bigram_prob}

    return class_model, word_count


# Train The Model For All Classes That Are Represented In The Train DataSet
def train_all_models():
    model = {}
    total_number_of_words = 0
    poet_count = {}
    for file in os.listdir("train_set"):
        if file.endswith(".txt"):
            file_addr = os.path.join("train_set", file)
            poet = file.split('_')[0]
            data = read_data(file_addr).readlines()
            class_model, word_count = train_model(data)
            model[poet] = class_model
            poet_count[poet] = word_count
            total_number_of_words += word_count

    model['PoetProb'] = {key: math.log2(val / total_number_of_words) for key, val in poet_count.items()}
    return model


# Calculate The Unigram Probability Of One Class For One Line In The Test DataSet
def calculate_unigram_of_line(line, unigram_model):
    words = line.split()
    unigram_prob = 1
    for w in words:
        if w in unigram_model.keys():
            unigram_prob *= 2 ** unigram_model[w]
        else:
            unigram_prob *= 0.00001

    return unigram_prob


# Calculate The Bigram Probability Of One Class For One Line In The Test DataSet
def calculate_bigram_of_line(line, bigram_model):
    edited = '<s> ' + line.replace('\n', '') + ' <\s>'
    words = edited.split()
    num_of_line_words = len(words)
    bigram_prob = 1
    for w in range(1, num_of_line_words):
        prob_name = words[w] + '|' + words[w - 1]
        if prob_name in bigram_model.keys():
            bigram_prob *= 2 ** bigram_model[prob_name]
        else:
            bigram_prob *= 0.00001

    return bigram_prob


# Calculate The Accuracy Of Trained Model By Predicting The Label Of The Test DataSet
def test_model(model, x, y, l1=0.001, l2=0.299, l3=0.7, eps=0.000001):
    num_of_data = len(y)
    tp_unigram = 0
    tp_bigram = 0
    tp_backoff = 0
    for i in range(num_of_data):
        max_prob_unigram = 0
        max_prob_bigram = 0
        max_prob_backoff = 0
        predicted_y_unigram = ''
        predicted_y_bigram = ''
        predicted_y_backoff = ''
        for k, v in model.items():
            if k != 'PoetProb':
                poet_prob = 2 ** model['PoetProb'][k]
                unigram_prob = poet_prob * calculate_unigram_of_line(x[i], v['Unigram'])
                bigram_prob = poet_prob * calculate_bigram_of_line(x[i], v['Bigram'])
                backoff_prob = l3 * bigram_prob + l2 * unigram_prob + l1 * eps

                if unigram_prob > max_prob_unigram:
                    max_prob_unigram = unigram_prob
                    predicted_y_unigram = k

                if max_prob_bigram < bigram_prob:
                    max_prob_bigram = bigram_prob
                    predicted_y_bigram = k

                if max_prob_backoff < backoff_prob:
                    max_prob_backoff = backoff_prob
                    predicted_y_backoff = k

        if predicted_y_unigram == y[i]:
            tp_unigram += 1

        if predicted_y_bigram == y[i]:
            tp_bigram += 1

        if predicted_y_backoff == y[i]:
            tp_backoff += 1

    unigram_accuracy = tp_unigram / num_of_data
    bigram_accuracy = tp_bigram / num_of_data
    backoff_accracy = tp_backoff / num_of_data
    return unigram_accuracy, bigram_accuracy, backoff_accracy


if __name__ == '__main__':
    Model = train_all_models()
    x_test, y_test = read_test_data('test_set\\test_file.txt')
    eps_choices = [0.001, 0.000001]
    lambda_choices = [(0.001, 0.233, 0.766), (0.00001, 0.23333, 0.76666), (0, 0.5, 0.5), (0, 0.001, 0.999)]
    for i in range(len(eps_choices)):
        for j in range(len(lambda_choices)):
            print('Accuracy Of Model With Parameters, eps =', eps_choices[i], 'lambas =', lambda_choices[j], 'Is:')
            params = lambda_choices[j]
            accuracy = test_model(Model, x_test, y_test, l1=params[0],
                                  l2=params[1], l3=params[2], eps=eps_choices[i])
            print('Unigram Accracy:', accuracy[0])
            print('Bigram Accracy:', accuracy[1])
            print('BackOff Accracy:', accuracy[2])
            print()
