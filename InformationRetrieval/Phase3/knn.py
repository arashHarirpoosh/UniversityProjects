import operator
import numpy as np


class KNN:

    def __init__(self, train_data, train_labels):
        self.train_data = train_data
        self.train_labels = train_labels

    def predict(self, test_data, k):
        distances = {}
        results = {}
        num_of_all_data = len(self.train_data)
        # for i in range(1, num_of_all_data + 1):
        for i in self.train_data.keys():
            # print(i)
            # print(len(self.train_data[str(i)]), len(test_data))
            # print(self.train_data)
            # print(i, len(test_data), len(self.train_data[i]))
            distances[int(i)] = np.linalg.norm(test_data - self.train_data[i])
        sorted_distances = {
            k: v for k, v in sorted(distances.items(), key=lambda item: item[1], reverse=False)
        }
        # print(sorted_distances)
        keys_list = list(sorted_distances.keys())
        for i in range(min(k, len(keys_list))):
            doc_num = keys_list[i] - 1
            doc_label = self.train_labels[doc_num]
            # print(doc_label)
            if doc_label not in results.keys():
                results[doc_label] = 0
            results[doc_label] = results[doc_label] + 1
        predicted_label = max(results.items(), key=operator.itemgetter(1))[0]
        return predicted_label
