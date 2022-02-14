import re
import os
import time
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from Phase3.knn import KNN
from Phase1.data import Data
import matplotlib.pyplot as plt
from Phase3.kmeans import KMeans
from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold
from Phase2.vectorization import Vectorization
from sklearn.metrics import accuracy_score, f1_score


class EnhancedSearch:

    def __init__(self, title, content, labels, volume_of_data):
        self.model = None
        self.title = title
        self.labels = labels
        self.clusters = None
        self.classifier = None
        self.content = content
        self.tfidf_scores = None
        self.labels_encoder = None
        self.clustering_model = None
        self.cluster_centroids = None
        self.all_docs_embedding = None
        self.volume_of_data = volume_of_data
        self.index_constructor = Data(title=title, content=content)
        self.vectorizer = Vectorization(title=title, content=content,
                                        total_number_of_docs=len(content))

    def prepare_word_embedding_model(self):
        model_addr_dir = f'Embeddings/{self.volume_of_data}'
        model_addr = f'{model_addr_dir}/w2v_300d_{self.volume_of_data}.h5'
        training_data_addr = f'training_data_{self.volume_of_data}.obj'
        if os.path.isfile(training_data_addr):
            td = self.vectorizer.load_pickel_data(training_data_addr)
        else:
            td = self.vectorizer.prepare_training_data()
            self.vectorizer.save_pickle_data(td, f'training_data_{self.volume_of_data}.obj')

        if not os.path.isdir(model_addr_dir):
            os.makedirs(model_addr_dir)
            self.vectorizer.train_word2vec_model(training_data=td, addr=model_addr)

        self.model = self.vectorizer.load_w2v_model(addr=model_addr)
        return self.model

    @staticmethod
    def read_tfidf_index(file_name):
        with open(file_name) as json_file:
            scores = json.load(json_file)
        return scores

    def load_documents_tfidf_scores(self):
        # tfidf_index_addr = f'Indexes/tfidf_index_{self.volume_of_data}.json'
        tfidf_index_addr = f'Indexes/tfidf/tfidf_index_{self.volume_of_data}.json'
        if os.path.isfile(tfidf_index_addr):
            # self.tfidf_scores = self.vectorizer.read_positional_index(file_name=tfidf_index_addr)
            self.tfidf_scores = self.read_tfidf_index(file_name=tfidf_index_addr)
        else:
            positional_index_addr = f'Indexes/positional_index_{self.volume_of_data}.json'
            if os.path.isfile(positional_index_addr):
                self.index_constructor.read_positional_index(file_name=positional_index_addr)
            else:
                self.index_constructor.generate_positional_index()
                self.index_constructor.save_positional_index(file_name=positional_index_addr)
            positional_index = self.index_constructor.positional_index
            self.tfidf_scores = self.vectorizer.calculate_all_docs_tfidf_separate_file(
                positional_index=positional_index,
                file_name=tfidf_index_addr)
            # self.vectorizer.save_positional_index(file_name=tfidf_index_addr)

    def construct_document_vectors(self):
        doc_embedding_addr = f'DocumentEmbeddings/document_vectors_{self.volume_of_data}.obj'
        if os.path.isfile(doc_embedding_addr):
            self.all_docs_embedding = self.vectorizer.load_pickel_data(addr=doc_embedding_addr)
        else:
            self.prepare_word_embedding_model()
            print('Model Loaded.')
            if self.vectorizer.model is None:
                model_addr = f'Embeddings/{self.volume_of_data}/w2v_300d_{self.volume_of_data}.h5'
                self.vectorizer.load_w2v_model(addr=model_addr)
            self.load_documents_tfidf_scores()
            print('tf-idf Scores Computed.')
            self.all_docs_embedding = self.vectorizer.generate_docs_vector(tfidf_scores=self.tfidf_scores)
            self.vectorizer.save_pickle_data(self.all_docs_embedding, addr=doc_embedding_addr)
        return self.all_docs_embedding

    def calculate_clusters(self, k, min_initial_centroids_dist):
        if self.all_docs_embedding is None:
            self.construct_document_vectors()
        # print(len(self.all_docs_embedding.values()))
        df = pd.DataFrame(list(self.all_docs_embedding.values()))
        # print(df)
        self.clustering_model = KMeans()
        centroids, clusters = self.clustering_model.clustering(data=df, k=k,
                                                               min_initial_centroids_dist=min_initial_centroids_dist)
        # print(centroids)
        clustering_result = {}
        for ci, point in clusters:
            if ci not in clustering_result.keys():
                clustering_result[ci] = []
            clustering_result[ci].append(point)
        self.clusters = clustering_result
        self.cluster_centroids = centroids
        clustering_result_addr = f'Clusters/{self.volume_of_data}'
        if not os.path.isdir(clustering_result_addr):
            os.makedirs(clustering_result_addr)
        self.vectorizer.save_pickle_data(clustering_result,
                                         addr=f'{clustering_result_addr}/clusters_{self.volume_of_data}_{k}.obj')

        self.vectorizer.save_pickle_data(centroids,
                                         addr=f'{clustering_result_addr}/centroids_{self.volume_of_data}_{k}.obj')
        # print(clustering_result)
        # print(clustering_model.plot_k_means_error(df, 10))
        # print(len(clusters[:, 0]), clusters[0][0])

    def calculate_tfidf_scores(self, positional_index):
        vec = {}
        for k, v in positional_index.items():
            # nt = len(self.vectorizer.tfidf_positional_index[k].keys()) - 1
            nt = len(self.tfidf_scores[k].keys())
            score = self.vectorizer.calculated_tfidf(nt, len(v))
            vec[k] = score
        return vec

    def construct_query_vector(self, query):
        # self.vectorizer.read_positional_index(file_name='Indexes/tfidf_index_11k.json')
        # if len(self.vectorizer.tfidf_positional_index) == 0:
        if self.tfidf_scores is None:
            self.load_documents_tfidf_scores()
        if self.model is None:
            self.prepare_word_embedding_model()

        tokens = self.vectorizer.query_preprocess(query, tfidf_scores=self.tfidf_scores)
        tokens = [x for x in tokens if x not in self.vectorizer.stop_words_list]
        pos_index = self.vectorizer.calculate_positional_index_query(tokens)
        vec = self.calculate_tfidf_scores(pos_index)
        query_vec = np.zeros(300)
        weights = 0
        for k, v in vec.items():
            score = vec[k]
            query_vec += self.model.wv[k] * score
            weights += score
        query_vec /= weights
        return query_vec

    def find_doc_id(self, doc_vec):
        if self.all_docs_embedding is None:
            self.construct_document_vectors()
        for i, d in self.all_docs_embedding.items():
            if (d == doc_vec).all():
                return i

    def preprocess_clusters(self):
        clusters = {}
        start = time.time()
        items = list(self.clusters.items())
        for i in tqdm(range(len(items))):
            k, v = items[i]
            if k not in clusters:
                clusters[k] = []
            points = list(v)
            for j in tqdm(range(len(points))):
                clusters[k].append(self.find_doc_id(v[j]))
        print(f'{time.time() - start}')
        return clusters

    def enhanced_query_with_clustering(self, query, k=5, b=1):
        start = time.time()
        if self.clusters is None:
            self.clusters = self.vectorizer.load_pickel_data(
                addr=f'Clusters/{self.volume_of_data}/clusters_{self.volume_of_data}_{k}.obj')
            # self.clusters = self.preprocess_clusters()
        print(f'Clusters Loaded in {time.time() - start} Seconds.')
        start = time.time()
        if self.cluster_centroids is None:
            self.cluster_centroids = self.vectorizer.load_pickel_data(
                addr=f'Clusters/{self.volume_of_data}/centroids_{self.volume_of_data}_{k}.obj')
        print(f'Centroids Loaded {time.time() - start} Seconds')
        start = time.time()

        query_vec = self.construct_query_vector(query=query)
        print(f'Query Vector constructed {time.time() - start} Seconds.')
        start = time.time()
        centroids_similarity = {}
        k = len(self.cluster_centroids)
        for c in range(k):
            centroids_similarity[c] = (self.vectorizer.calculate_cosine_similarity(self.cluster_centroids[c],
                                                                                   query_vec) + 1) / 2
        sorted_centroids = {
            k: v for k, v in sorted(centroids_similarity.items(), key=lambda item: item[1], reverse=True)
        }
        print(sorted_centroids)
        doc_similarities = {}
        for ki in range(b):
            ci = list(sorted_centroids.keys())[ki]
            centroid = self.cluster_centroids[ci]
            # print(ci)
            print(len(self.clusters[ci]))
            # i = 0
            for p in self.clusters[ci]:
                s = time.time()
                sim = self.vectorizer.calculate_cosine_similarity(query_vec, p)
                doc_similarities[self.find_doc_id(p)] = (sim + 1) / 2
                # print(time.time() - s)

                # print(self.find_doc_id(p))
                # i += 1
                # print(i)
        sorted_doc_results = {
            k: v for k, v in sorted(doc_similarities.items(), key=lambda item: item[1], reverse=True)
        }
        print(f'Query Processed in {time.time() - start} Seconds.')
        return sorted_doc_results

    def label_encoding(self):
        self.labels_encoder = preprocessing.LabelEncoder()
        self.labels = self.labels_encoder.fit_transform(self.labels)
        # print(self.labels_encoder.inverse_transform([0, 1, 2, 3, 4]))
        return self.labels

    def enhanced_query_with_classification(self, query):
        start = time.time()
        if self.labels_encoder is None:
            self.label_encoding()
        if self.classifier is None:
            if self.all_docs_embedding is None:
                self.construct_document_vectors()
            self.classifier = KNN(train_data=self.all_docs_embedding, train_labels=self.labels)
        print(f'Required Files Loaded in {time.time() - start} Seconds.')
        start = time.time()
        # print(re.findall(r'cat:(\w+) ([\w|\s]+)', query))
        category, query_content = re.findall(r'cat:(\w+) ([\w|\s]+)', query)[0]
        print(category, query_content)
        category_index = self.labels_encoder.transform([category])[0]
        related_docs = self.content[self.labels == category_index]
        print(f'{len(related_docs)} docs in the category of {category}')
        query_vec = self.construct_query_vector(query=query_content)
        print(f'Query Vector constructed {time.time() - start} Seconds.')
        start = time.time()
        related_docs_key = related_docs.keys()
        doc_similarities = {}
        for d in related_docs_key:
            # print(d)
            doc = self.all_docs_embedding[str(d + 1)]
            sim = self.vectorizer.calculate_cosine_similarity(query_vec, doc)
            doc_similarities[self.find_doc_id(doc_vec=doc)] = (sim + 1) / 2
            # print(self.find_doc_id(p))
        sorted_doc_results = {
            k: v for k, v in sorted(doc_similarities.items(), key=lambda item: item[1], reverse=True)
        }
        print(f'Query Processed in {time.time() - start} Seconds.')
        return sorted_doc_results

    def classify_document(self, document, k):
        if self.labels_encoder is None:
            self.label_encoding()
        if self.classifier is None:
            if self.all_docs_embedding is None:
                self.construct_document_vectors()
            self.classifier = KNN(train_data=self.all_docs_embedding, train_labels=self.labels)

        doc_vector = self.construct_query_vector(query=document)
        predicted_doc_label = self.classifier.predict(test_data=doc_vector, k=k)
        return self.labels_encoder.inverse_transform([predicted_doc_label])[0]

    def classify_all_documents(self, df_all_documents, k):
        num_of_all_docs = len(df_all_documents)
        print(num_of_all_docs)
        df_all_documents['category'] = None
        for d in tqdm(range(num_of_all_docs), desc='Loading'):
            doc = df_all_documents.iloc[d]
            # print(1)
            df_all_documents.loc[d]['category'] = self.classify_document(document=doc['content'], k=k)
            # print(doc)
        classification_res_addr = f'Classification/{self.volume_of_data}'
        if not os.path.isdir(classification_res_addr):
            os.makedirs(classification_res_addr)
        classification_res_addr = f'{classification_res_addr}/classification_res_{self.volume_of_data}_{k}.xlsx'
        df_all_documents.to_excel(classification_res_addr)

    def evaluate_classifier(self, k):
        # self.label_encoding()
        if self.all_docs_embedding is None:
            self.construct_document_vectors()
        if self.labels_encoder is None:
            self.label_encoding()
        print('Loaded.')
        kf = KFold(n_splits=10)
        number_of_data = len(self.all_docs_embedding)
        accuracy = []
        all_f1_score = []
        for train, test in kf.split(range(number_of_data)):
            x_train = {str(k + 1): self.all_docs_embedding[str(k + 1)] for k in train}
            y_train = {k: self.labels[k] for k in train}
            x_test = {str(k + 1): self.all_docs_embedding[str(k + 1)] for k in test}
            y_test = {k: self.labels[k] for k in test}
            knn_classifier = KNN(train_data=x_train, train_labels=y_train)
            y_predicted = []
            for x in x_test:
                y_predicted.append(knn_classifier.predict(test_data=self.all_docs_embedding[x], k=k))
            y_true = list(y_test.values())
            acc = accuracy_score(y_true=y_true, y_pred=y_predicted)
            f = f1_score(y_true=y_true, y_pred=y_predicted, average='macro')
            print(f'Accuracy: {acc}, f1_score: {f}')
            accuracy.append(acc)
            all_f1_score.append(f)
            print(100 * '-')
        avg_acc = np.mean(accuracy)
        avg_f1 = np.mean(all_f1_score)
        x = range(len(accuracy))
        plt.plot(x, [100 * acc for acc in accuracy], label='Accuracy')
        plt.plot(x, [100 * f for f in all_f1_score], label='F1 Score')
        plt.legend(loc="upper left")
        plt.show()
        print(f'AVG Accuracy: {avg_acc}, AVG F1 Score: {avg_f1}')

    @staticmethod
    def reduce_dimension_to_2d(data):
        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(np.array(list(data)))
        return principal_components

    def plot_cluster(self, k=5):
        if self.clusters is None or self.cluster_centroids is None:
            self.clusters = self.vectorizer.load_pickel_data(
                addr=f'Clusters/{self.volume_of_data}/clusters_{self.volume_of_data}_{k}.obj')
            self.cluster_centroids = self.vectorizer.load_pickel_data(
                addr=f'Clusters/{self.volume_of_data}/centroids_{self.volume_of_data}_{k}.obj')
        centroids_2d = self.reduce_dimension_to_2d(self.cluster_centroids)
        clusters_2d = {}
        for k, v in self.clusters.items():
            clusters_2d[k] = self.reduce_dimension_to_2d(v)
        print(clusters_2d)
        model = KMeans(df=self.content)
        model.plot_cluster(cntr=centroids_2d, cluster=clusters_2d)

    def plot_document_embeddings(self):
        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(np.array(list(self.all_docs_embedding.values())))
        pc1 = principal_components[:, 0]
        pc2 = principal_components[:, 1]
        plt.scatter(pc1, pc2)
        plt.show()
