import time
import json
import pickle
from hazm import *
import numpy as np
import multiprocessing
from gensim.models import Word2Vec


class Vectorization:
    def __init__(self, title, content, total_number_of_docs):
        self.model = None
        self.title = title
        self.content = content
        self.champion_list = None
        self.all_docs_vec = None
        self.ir_stemmer = Stemmer()
        self.tfidf_positional_index = {}
        self.ir_normalizer = Normalizer()
        self.ir_lemmatizer = Lemmatizer()
        self.stop_words_list = stopwords_list()
        self.total_number_of_docs = total_number_of_docs

    # Calculate the tfidf
    def calculated_tfidf(self, nt, ftd):
        return (1 + np.log(ftd)) * np.log(self.total_number_of_docs / nt)

    # Calculate the tfidf score for all of the tokens in the documents
    def calculate_all_docs_tfidf(self, positional_index):
        for k, v in positional_index.items():
            if k not in self.tfidf_positional_index.keys():
                self.tfidf_positional_index[k] = {'total_num': v['total_num']}

            for doc_num in list(v)[1:]:
                token_index = positional_index[k]
                nt = len(token_index.keys()) - 1
                ftd = len(token_index[doc_num])
                if type(token_index[doc_num]) != list:
                    ftd = len(token_index[doc_num].loc)
                self.tfidf_positional_index[k][doc_num] = {
                    'loc': v[doc_num],
                    'tfidf': self.calculated_tfidf(nt, ftd)
                }

    def calculate_all_docs_tfidf_separate_file(self, positional_index, file_name):
        tfidf_scores = {}
        for k, v in positional_index.items():
            for doc_num in list(v)[1:]:
                if k not in tfidf_scores:
                    tfidf_scores[k] = {}

                token_index = positional_index[k]
                nt = len(token_index.keys()) - 1
                ftd = len(token_index[doc_num])
                if type(token_index[doc_num]) != list:
                    ftd = len(token_index[doc_num].loc)
                tfidf_scores[k][doc_num] = self.calculated_tfidf(nt, ftd)
        with open(file_name, 'w') as fp:
            json.dump(tfidf_scores, fp, indent=4)
        return tfidf_scores

    # Save the Generated Positional Indexed so that It could be used next time
    def save_positional_index(self, file_name='positionalIndex_tfidf.json'):
        with open(file_name, 'w') as fp:
            json.dump(self.tfidf_positional_index, fp, indent=4)

    # Read the Positional Index that Generated in the past
    def read_positional_index(self, file_name='positionalIndex_tfidf.json'):
        with open(file_name) as json_file:
            self.tfidf_positional_index = json.load(json_file)

    # Generate the champion list for the tokens based on their tfidf scores
    def construct_champion_list(self, r):
        champion_list = {}
        for k, v in self.tfidf_positional_index.items():
            all_terms_doc_score = {d: self.tfidf_positional_index[k][d]['tfidf']
                                   for d in self.tfidf_positional_index[k].keys() if d != 'total_num'}
            all_terms_doc_score = sorted(all_terms_doc_score.items(), key=lambda x: x[1], reverse=True)
            champion_list[k] = dict(all_terms_doc_score[:min(r, len(all_terms_doc_score))])
        self.champion_list = champion_list
        return champion_list

    # Save the Generated champion_list so that It could be used next time
    def save_champion_list(self, file_name='champion_list.json'):
        with open(file_name, 'w') as fp:
            json.dump(self.champion_list, fp, indent=4)

    # Read the champion_list that Generated in the past
    def read_champion_list(self, file_name='champion_list.json'):
        with open(file_name) as json_file:
            self.champion_list = json.load(json_file)

    # Calculate the cosine similarity of two vectors
    @staticmethod
    def calculate_cosine_similarity(a, b):
        return np.dot(a, b) / (np.sqrt(np.dot(a, a) * np.dot(b, b)))

    # PreProcess the Given Query
    def query_preprocess(self, tokens, tfidf_scores=None):
        if tfidf_scores is None:
            tfidf_scores = self.tfidf_positional_index
        base_form_words = []
        word = word_tokenize(tokens)
        for w in word:
            stem_tokens = self.ir_stemmer.stem(w)
            lem_tokens = self.ir_lemmatizer.lemmatize(stem_tokens)
            if lem_tokens in tfidf_scores.keys():
                base_form_words.append(lem_tokens)
        return base_form_words

    # Calculate the positional index for the given query
    @staticmethod
    def calculate_positional_index_query(tokens):
        pos_index = {}
        pos = 0
        for t in tokens:
            if t not in pos_index.keys():
                pos_index[t] = []
            pos_index[t].append(pos)
            pos += 1
        return pos_index

    # Calculate the vector of the given positional index of the query
    def calculate_query_vector(self, positional_index):
        vec = []
        for k, v in positional_index.items():
            nt = len(self.tfidf_positional_index[k].keys()) - 1
            score = self.calculated_tfidf(nt, len(v))
            vec.append(score)
        return vec

    # Calculate the vector for the specific document
    def calculate_doc_vector(self, tokens, doc_num):
        vec = []
        for t in tokens:
            if doc_num in self.tfidf_positional_index[t]:
                vec.append(self.tfidf_positional_index[t][doc_num]['tfidf'])
            else:
                vec.append(0)
        return vec

    # Perform the search of the given query
    def retrieve_query(self, query):
        tokens = self.query_preprocess(query)
        tokens = [x for x in tokens if x not in self.stop_words_list]
        pos_index = self.calculate_positional_index_query(tokens)
        vec = self.calculate_query_vector(pos_index)
        doc_similarities = {}
        champion_list_docs = []
        for t in tokens:
            [champion_list_docs.append(d) for d in self.champion_list[t].keys() if d not in champion_list_docs]

        for i in champion_list_docs:
            doc_vec = self.calculate_doc_vector(tokens, str(i))
            if np.sum(doc_vec) > 0:
                similarity = self.calculate_cosine_similarity(vec, doc_vec)
                if similarity > 0:
                    doc_similarities[i] = similarity

        sorted_similarities = \
            {
                k: v for k, v in sorted(doc_similarities.items(), key=lambda item: item[1], reverse=True)
            }
        return sorted_similarities

    # Return the sentence of the Given Word in the Specific Document
    def find_sentence(self, doc_id, tokens):
        all_sent = sent_tokenize(self.content.iloc[doc_id])
        res = []
        for s in all_sent:
            existence = any(elem in s.split() for elem in tokens)
            if existence:
                res.append(s)
        return res

    # Print the given results
    def print_k_results(self, results, k, query):
        selected_keys = list(results.keys())[:k]
        tokens = query.split()
        for d in selected_keys:
            ind = int(d) - 1
            print(f'Doc ID: {ind}, Doc Title: {self.title[ind]}, Similarity: {results[d]}')
            all_sentences = self.find_sentence(ind, tokens)
            for s in all_sentences:
                print(s)
                print(100 * '-')
            print(100 * '+')

    def prepare_training_data(self):
        training_data = []
        for s in self.content:
            content_tokens = []
            norm_sent = self.ir_normalizer.normalize(s)
            sent_tokens = word_tokenize(norm_sent)
            for t in sent_tokens:
                stem_tokens = self.ir_stemmer.stem(t)
                final_tokens = self.ir_lemmatizer.lemmatize(stem_tokens)
                content_tokens.append(final_tokens)
            training_data.append(content_tokens)
        return training_data

    def save_pickle_data(self, data, addr):
        with open(addr, 'wb') as f:
            pickle.dump(data, f)

    def load_pickel_data(self, addr):
        with open(addr, 'rb') as f:
            data = pickle.load(f)
        return data

    def train_word2vec_model(self, training_data, addr='w2v_300d.h5'):
        cores = multiprocessing.cpu_count()
        print(f'Num of cores: {cores}')
        w2v_model = Word2Vec(
            min_count=1,
            window=5,
            vector_size=300,
            alpha=0.03,
            workers=cores - 1
        )
        w2v_model.build_vocab(training_data)
        print(f'Number of vocabs: {len(w2v_model.wv)}')
        start = time.time()
        w2v_model.train(training_data, total_examples=w2v_model.corpus_count, epochs=25)
        print(f'Training time: {time.time() - start} S')
        w2v_model.save(addr)

    def load_w2v_model(self, addr='w2v_300d.h5'):
        self.model = Word2Vec.load(addr)
        return self.model

    def generate_docs_vector(self, tfidf_scores=None):
        if tfidf_scores is None:
            tfidf_scores = self.tfidf_positional_index
        doc_num = 1
        all_docs_vec = {}
        if self.model is None:
            self.load_w2v_model()

        for s in self.content:
            norm_sent = self.ir_normalizer.normalize(s)
            sent_tokens = word_tokenize(norm_sent)
            sent_tokens = [x for x in sent_tokens if x not in self.stop_words_list]
            doc_vec = np.zeros(300)
            weights = 0
            for t in sent_tokens:
                stem_tokens = self.ir_stemmer.stem(t)
                final_tokens = self.ir_lemmatizer.lemmatize(stem_tokens)
                if final_tokens in tfidf_scores.keys() and final_tokens in self.model.wv:
                    # print(self.tfidf_positional_index[final_tokens].keys(), doc_num)
                    # print(final_tokens)
                    token_score = tfidf_scores[final_tokens][str(doc_num)]
                    if type(token_score) == dict:
                        token_score = tfidf_scores[final_tokens][str(doc_num)]['tfidf']
                    doc_vec += self.model.wv[final_tokens] * token_score
                    weights += token_score
            all_docs_vec[str(doc_num)] = doc_vec / weights
            doc_num += 1
        return all_docs_vec

    def load_all_docs_vec(self, addr='docs_vec.obj'):
        self.all_docs_vec = self.load_pickel_data(addr)

    def test_w2v_model(self, query):
        tokens = self.query_preprocess(query)
        tokens = [x for x in tokens if x not in self.stop_words_list]
        pos_index = self.calculate_positional_index_query(tokens)
        vec = self.calculate_query_vector(pos_index)
        query_vec = np.zeros(300)
        weights = 0
        if self.model is None:
            self.load_w2v_model()

        if self.all_docs_vec is None:
            self.load_all_docs_vec()

        if self.champion_list is None:
            self.read_champion_list()

        for tn in range(len(tokens)):
            score = vec[tn]
            query_vec += self.model.wv[tokens[tn]] * score
            weights += score
        query_vec /= weights

        doc_similarities = {}
        champion_list_docs = []
        for t in tokens:
            [champion_list_docs.append(d) for d in self.champion_list[t].keys() if d not in champion_list_docs]

        for i in champion_list_docs:
            similarity = self.calculate_cosine_similarity(self.all_docs_vec[i], query_vec)
            similarity = (similarity + 1) / 2
            if similarity > 0:
                doc_similarities[i] = similarity

        sorted_similarities = \
            {
                k: v for k, v in sorted(doc_similarities.items(), key=lambda item: item[1], reverse=True)
            }
        return sorted_similarities
