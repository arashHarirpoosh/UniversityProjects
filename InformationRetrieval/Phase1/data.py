import json
import numpy as np
from hazm import *
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


class Data:
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.ir_normalizer = Normalizer()
        self.ir_stemmer = Stemmer()
        self.ir_lemmatizer = Lemmatizer()
        self.stop_words_list = stopwords_list()
        self.positional_index = {}

    # Generate Positional Index for the Given Content
    def generate_positional_index(self, remove_stopwords=True):
        self.positional_index = {}
        doc_num = 1

        for s in self.content:
            norm_sent = self.ir_normalizer.normalize(s)
            sent_tokens = word_tokenize(norm_sent)
            if remove_stopwords:
                sent_tokens = [x for x in sent_tokens if x not in self.stop_words_list]

            pos_num = 1
            for t in sent_tokens:
                stem_tokens = self.ir_stemmer.stem(t)
                final_tokens = self.ir_lemmatizer.lemmatize(stem_tokens)
                if final_tokens not in self.positional_index.keys():
                    self.positional_index[final_tokens] = {'total_num': 0}
                if doc_num not in self.positional_index[final_tokens].keys():
                    self.positional_index[final_tokens][doc_num] = []
                self.positional_index[final_tokens][doc_num].append(pos_num)
                self.positional_index[final_tokens]['total_num'] += 1
                pos_num += 1
            # print(doc_num, doc_num / len(self.content))
            doc_num += 1

    # Save the Generated Positional Indexed so that It could be used next time
    def save_positional_index(self, file_name='positionalIndex.json'):
        with open(file_name, 'w') as fp:
            json.dump(self.positional_index, fp, indent=4)

    # Read the Positional Index that Generated in the past
    def read_positional_index(self, file_name='positionalIndex.json'):
        with open(file_name) as json_file:
            self.positional_index = json.load(json_file)

    # Query One word from Positional Index
    def retrieve_one_word(self, word):
        stem_tokens = self.ir_stemmer.stem(word)
        final_tokens = self.ir_lemmatizer.lemmatize(stem_tokens)
        return self.positional_index[final_tokens]

    # Find Common Numbers Between Two List
    def find_common_numbers(self, pos1, pos2):
        common_docs = []
        for doc_num in pos1:
            if doc_num in pos2 and doc_num != 'total_num':
                common_docs.append(doc_num)
        return common_docs

    # PreProcess the Given Query
    def query_preprocess(self, tokens):
        base_form_words = []
        word = word_tokenize(tokens)
        for w in word:
            stem_tokens = self.ir_stemmer.stem(w)
            base_form_words.append(self.ir_lemmatizer.lemmatize(stem_tokens))
        return base_form_words

    # Query Bi-words from Positional Index
    def retrieve_bi_word(self, bi_word):
        first_word, second_word = self.query_preprocess(bi_word)
        pos1 = self.positional_index[first_word]
        pos2 = self.positional_index[second_word]
        res = {}
        if len(pos1.keys()) <= len(pos2.keys()):
            common_docs = self.find_common_numbers(pos1.keys(), pos2.keys())
        else:
            common_docs = self.find_common_numbers(pos2.keys(), pos1.keys())

        # Retrieve exact same pattern
        for doc_num in common_docs:
            if len(pos1[doc_num]) <= len(pos2[doc_num]):
                ind1 = np.array(pos1[doc_num])
                ind2 = np.array(pos2[doc_num]) - 1
            else:
                ind1 = np.array(pos2[doc_num]) - 1
                ind2 = np.array(pos1[doc_num])

            for dn in ind1:
                if dn in ind2:
                    if doc_num not in res.keys():
                        res[doc_num] = []
                    res[doc_num].append(max(0, dn))
        return res

    # Query Phrases with More than Two Words
    def retrieve_n_words(self, n_words):
        words = word_tokenize(n_words)
        list_of_bi_words = []
        res = {}
        for wi in range(1, len(words)):
            new_bi_word = f'{words[wi - 1]} {words[wi]}'
            list_of_bi_words.append(new_bi_word)
        # print(list_of_bi_words[0])
        # print(list_of_bi_words[1])
        bi_word_indexes = {}
        for bw in list_of_bi_words:
            bi_word_indexes[bw] = self.retrieve_bi_word(bw)

        docs_with_common_bi_words = self.find_common_numbers(bi_word_indexes[list_of_bi_words[0]],
                                                             bi_word_indexes[list_of_bi_words[1]])
        for n in range(2, len(bi_word_indexes.keys())):
            docs_with_common_bi_words = self.find_common_numbers(bi_word_indexes[list_of_bi_words[n]],
                                                                 docs_with_common_bi_words)
        for doc_num in docs_with_common_bi_words:
            all_ind = []
            for i in range(len(list_of_bi_words)):
                all_ind.append(np.array(bi_word_indexes[list_of_bi_words[i]][doc_num]) - i)

            c = np.intersect1d(all_ind[0], all_ind[1])
            for j in range(2, len(all_ind)):
                c = np.intersect1d(c, all_ind[j])
            if len(c) > 0:
                res[doc_num] = c

        return res

    # Return the sentence of the Given Word in the Specific Document
    def find_sentence(self, doc_id, word_pose, remove_stopwords=False):
        # seprators = ['.', ',', ';']
        # beginning = word_pose
        # ending = word_pose
        # doc_content = word_tokenize(self.content.iloc[doc_id])
        # sentence = ''
        # while doc_content[beginning] not in seprators and beginning > 0:
        #     beginning -= 1
        # while doc_content[ending] not in seprators and ending < len(doc_content):
        #     ending += 1
        # for i in range(beginning, ending):
        #     sentence += ' ' + doc_content
        all_sent = sent_tokenize(self.content.iloc[doc_id])

        word_num = 0
        for s in all_sent:
            all_words = word_tokenize(s)
            if remove_stopwords:
                all_words = [x for x in all_words if x not in self.stop_words_list]

            for w in all_words:
                word_num += 1
                if word_num == word_pose:
                    return s
        return all_sent[-1]

    # Print the Result of the Queries
    def print_result(self, res, remove_stopwords=False):
        if type(res) == dict:
            itr = res.keys()
        else:
            itr = res
        print(res)
        for r in itr:
            if r != 'total_num':
                ind = int(r) - 1
                print(f'Doc ID: {ind}, Doc Title: {self.title[ind]}')
                for w in res[r]:
                    sent = self.find_sentence(ind, w - 1, remove_stopwords)
                    print('\n' + sent + '\n')
                    print(250 * '-')
                print(250 * '-')

    # Return the List Include the Number of Times the Token Repeated Sorted Based on their Rank
    def rank_tokens(self):
        rank_tokens = {}
        for k, v in self.positional_index.items():
            rank_tokens[k] = v['total_num']
        # rank_tokens = sorted(rank_tokens.items(), key=lambda item: item[1])
        rank_tokens = {k: v for k, v in sorted(rank_tokens.items(), key=lambda item: item[1], reverse=True)}

        return rank_tokens

    # Plot the Zipf's Law
    def plot_zipf_law(self, plot_title='Zipf Law'):
        act_val = list(self.rank_tokens().values())
        pred_val = []
        y = []
        x = []
        for i in range(1, len(act_val)):
            t = np.log10(i)
            x.append(t)
            # pred_val.append(np.log10(1 / i))
            pred_val.append(np.log10(act_val[0]) - t)
            y.append(np.log10(act_val[i - 1]))

        plt.plot(x, y, label='Actual value')
        plt.plot(x, pred_val, label='Predicted value')
        plt.legend()
        plt.xlabel('Log10 rank')
        plt.ylabel('Log10 cf')
        plt.title(plot_title)
        plt.show()

    # Calculate the Number of Tokens and Vocabs in the Specific Number of Documents
    def calculate_len_tokens(self, list_of_sizes, remove_stopwords):
        all_tokens = 0
        unique_tokens = []
        act_val_total = []
        act_val_unique = []
        # all_doc = len(self.content)
        all_doc = max(list_of_sizes) + 1
        for i in range(all_doc):
            doc_tokens = word_tokenize(self.content.iloc[i])
            for t in doc_tokens:
                if remove_stopwords:
                    t = [x for x in t if x not in self.stop_words_list]
                all_tokens += len(t)
                if t not in unique_tokens:
                    unique_tokens.append(t)
            if i in list_of_sizes:
                act_val_total.append(all_tokens)
                act_val_unique.append(len(unique_tokens))

        return act_val_total, act_val_unique

    # define the true objective function
    def objective(self, x, a, b):
        return a * x + b

    # Return the Total Number of Vocabs in All of the Documents
    def get_len_vocabs(self):
        return len(self.positional_index.keys())

    # Return the Total Number of Tokens in All of the Documents
    def get_len_tokens(self):
        sum_vocab = 0
        for k, v in self.positional_index.items():
            sum_vocab += v['total_num']
        return sum_vocab

    # Plot the Heap's Law
    def plot_heaps_law(self, list_of_sizes, remove_stopwords=False, plot_title='Heaps Law'):
        list_of_sizes.sort()
        act_val_token, act_val_vocab = self.calculate_len_tokens(list_of_sizes, remove_stopwords)
        all_vocab_sum, all_tokens_sum = self.get_len_vocabs(), self.get_len_tokens()
        act_val_vocab, act_val_token = np.log10(act_val_vocab), np.log10(act_val_token)

        popt, _ = curve_fit(self.objective, act_val_token, act_val_vocab)
        # summarize the parameter values
        a, b = popt
        print('y = %.5f * x + %.5f' % (a, b))
        print(f'All vocab numbers: {all_vocab_sum}, All token numbers: {all_tokens_sum}')
        print(f'Predicted all vocab numbers: {10 ** self.objective(np.log10(all_tokens_sum), a, b)}')

        x, y = [], []
        for i in range(len(act_val_vocab)):
            x.append(act_val_token[i])
            y.append(self.objective(act_val_token[i], a, b))

        plt.plot(act_val_token, act_val_vocab, label='Actual value')
        plt.plot(x, y, '--', color='red', label='Fitted line')
        plt.legend()
        plt.xlabel('Log10 T')
        plt.ylabel('Log10 M')
        plt.title(plot_title)
        plt.show()
