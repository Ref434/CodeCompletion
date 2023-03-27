import pandas as pd
from math import *
import numpy as np
import json
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestCentroid
from sklearn.cluster import SpectralClustering
from sklearn.cluster import DBSCAN
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.cluster import AffinityPropagation
from sklearn import metrics

from enum import Enum
import pickle

from operator import itemgetter

from thefuzz import fuzz as f

from code_completion_lib.necessary_functions import read_json, find_imported_methods

from code_completion_lib.logger.logger import Logger


class Cluster(Enum):
    STRUCTURED_DATA = 0                                 # ['numpy', 'matplotlib']
    SCIENTIFIC_COMPUTING = 1                            # ['pandas']
    REQUESTS = 2                                        # ['pandas', 'requests', 'bs4']
    SCIKIT_LEARN = 3                                    # ['numpy', 'pandas', 'scipy', 'matplotlib']
    SCIKIT_LEARN_VISUALIZATION = 4                      # ['numpy', 'pandas', 'sklearn', 'matplotlib', 'seaborn']
    TENSOR_FLOW = 5                                     # ['tensorflow', 'numpy', 'matplotlib']
    STRUCTURED_DATA_VISUALIZATION = 6                   # ['numpy', 'os', 'pandas', 'matplotlib']
    NUMPY_VISUALIZATION = 7                             # ['numpy', 'pandas', 'sklearn', 'matplotlib']
    DEEP_NEURAL_NETWORKS = 8                            # ['numpy', 'matplotlib', 'torch', 'torchvision']
    SCIKIT_LEARN_WITH_NATURAL_LANGUAGE_PROCESSING = 9   # ['numpy', 'pandas', 'sklearn', 'matplotlib', 'nltk', 're']
    STRUCTURED_DATA_VISUALIZATION_2 = 10                # ['numpy', 'pandas', 'matplotlib']
    IPython = 11                                        # ['IPython']
    CS771 = 12                                          # ['numpy', 'random', 'matplotlib', 'time']


class CodeCompletion:

    model = None
    df = None

    def __init__(self):
        self.logger = Logger(__name__)
        self.df = pd.read_csv(r'code_completion_lib\imports\preprocessing_imports.csv')

    def get_variable_completion(self, variable_name: str, imports: list, number: int = 5):
        cluster_variable = read_json(r'code_completion_lib\methods\relations_cluster_with_variable.json')

        cluster_name = self.cluster_predict(imports)

        variables: dict = {}
        result: list = []

        for name, value in cluster_variable[cluster_name].items():
            if name.startswith(variable_name):
                variables[name] = value
        sorted_variables = dict(sorted(variables.items(), key=itemgetter(1)))

        for variable in sorted_variables.keys():
            result.append(variable)

        result.reverse()

        return result[:number]

    def get_function_completion(self, variable_name: str, imports_lib: list, full_imports: list, number: int = 5):
        variable_method = read_json(r'code_completion_lib\methods\relations_variable_with_method.json')

        cluster_name: str = self.cluster_predict(imports_lib)

        # result for plugin: list[suggestion considering the imports | class for this suggestion]
        result: list = []

        best_score = 0
        best_match = 'p'
        for variable in variable_method.keys():
            score = f.WRatio(variable, variable_name)
            if score > best_score:
                best_score = score
                best_match = variable

        if cluster_name in variable_method[best_match].keys():
            methods = variable_method[best_match][cluster_name]
        else:
            cluster_name = list(variable_method[best_match].keys())[0]
            methods = variable_method[best_match][cluster_name]

        sorted_methods = dict(sorted(methods.items(), key=itemgetter(1)))

        imports = []
        for element in full_imports:
            imports.append(element.split("|"))

        imported_methods = find_imported_methods(list(sorted_methods), imports)
        for key in imported_methods.keys():
            if key[0] == key[1]:
                result.append(f"{key[1]}| ")
            else:
                result.append(f"{key[1]}|{key[0].replace(f'.{key[1]}', ' ')}")

        result.reverse()

        return result[:number]

    def relations_variable_with_method(self):
        df = pd.read_csv(r'code_completion_lib/methods/methods.csv')
        variable_method: dict = {}

        # Adding variables
        for line in df.values:
            variable_method[line[0]] = {}

        # Adding clusters
        for line in df.values:
            variable_method[line[0]][line[2]] = {}

        # Adding methods with their frequency
        for line in df.values:
            if line[1] in variable_method[line[0]][line[2]].keys():
                variable_method[line[0]][line[2]][line[1]] += 1
            else:
                variable_method[line[0]][line[2]][line[1]] = 1

        # Calculating the probability
        for cluster in variable_method.values():

            for method in cluster.values():
                total = 0
                for name, value in method.items():
                    total += value

                for name, value in method.items():
                    method[name] /= total

        with open('code_completion_lib/methods/relations_variable_with_method.json', 'w', encoding='utf-8') as f:
            json.dump(variable_method, f, ensure_ascii=False, indent=4)

    def relations_cluster_with_variable(self):
        df = pd.read_csv('code_completion_lib/methods/methods.csv')
        cluster_variable: dict = {}

        # Adding clusters
        for line in df.values:
            cluster_variable[line[2]] = {}

        # Adding variables with their frequency
        for line in df.values:
            if line[0] in cluster_variable[line[2]].keys():
                cluster_variable[line[2]][line[0]] += 1
            else:
                cluster_variable[line[2]][line[0]] = 1

        # Calculating the probability
        for variable in cluster_variable.values():
            total = 0
            for name, value in variable.items():
                total += value

            for name, value in variable.items():
                variable[name] /= total

        with open('code_completion_lib/methods/relations_cluster_with_variable.json', 'w', encoding='utf-8') as f:
            json.dump(cluster_variable, f, ensure_ascii=False, indent=4)

    def import_clusterization(self):

        # List for saving as .txt file
        result = []

        df = self.df.iloc[:, 1:]
        X = df.values[:, 1:]

        result.append(f"{len(df)} notebooks")

        tmp = df.copy()

        centroids_result = []

        cluster_model = AgglomerativeClustering(n_clusters=13, affinity='euclidean', linkage='ward')
        # cluster_model = DBSCAN(eps=0.1, min_samples=150)
        # cluster_model = SpectralClustering(n_clusters=20, assign_labels='discretize', random_state=0)
        # cluster_model = MeanShift()
        # cluster_model = AffinityPropagation(random_state=5)
        y_predict = cluster_model.fit_predict(X)
        labels = cluster_model.labels_

        # Metrics
        result.append(
            "Silhouette Coefficient: %0.3f"
            % metrics.silhouette_score(X, labels, metric="euclidean")
        )
        result.append(
            "Davies-Bouldin Index: %0.3f"
            % metrics.davies_bouldin_score(X, labels)
        )

        tmp.insert(0, 'labels', labels)
        result.append("labels:")
        result.append(tmp.groupby(['labels'])['filename'].count().tolist())

        clf = NearestCentroid()
        clf.fit(X, y_predict)
        centroids = clf.centroids_

        # Saving model
        pickle.dump(clf, open(r"code_completion_lib\model", 'wb'))

        # Finding the best example for each cluster by the Euqlidean distance to the cluster center
        for center in centroids:
            best_distance = 30
            best_filename = None
            for notebook in df.values:
                notebook_list = notebook.tolist()
                filename = notebook_list.pop(0)
                distance = np.sqrt(sum(pow(a - b, 2) for a, b in zip(center, notebook_list)))
                if distance < best_distance:
                    best_distance = distance
                    best_filename = filename

            centroids_result.append([best_filename, best_distance])

        result.append(f"found {len(centroids_result)} clusters")

        # Finding imports for the best example of each cluster
        all_imports = [column for column in df if column != "filename"]

        j = 0
        for notebook in centroids_result:
            imports = []
            import_vector = df.loc[df['filename'] == notebook[0]].values[:, 1:]
            for i in range(len(import_vector[0])):
                if import_vector[0][i] == 1:
                    imports.append(all_imports[i])
            result.append(
                f"{notebook[0]} {(15 - len(notebook[0])) * ' '} {notebook[1]} {(20 - len(f'{notebook[1]}')) * ' '} {Cluster(j).name} {(45 - len(Cluster(j).name)) * ' '} {imports}")
            j += 1

        with open(r"analysis\imports\import_clusterization.txt", "w") as file:
            for line in result:
                file.write(f"{line}\n")

        self.logger.info('Clusterization ended')

    def load_clusterization_model(self, filename):
        self.model = pickle.load(open(filename, 'rb'))

    def cluster_predict(self, imports: list) -> str:
        """Predict cluster for one notebook by imports"""
        self.load_clusterization_model(r"code_completion_lib\model")

        df = self.df.iloc[:, 2:]
        all_imports = [column for column in df if column != "filename"]

        X = [[]]

        # Made vector of imports
        for element in all_imports:
            if element in imports:
                X[0].append(1)
            else:
                X[0].append(0)

        predict = self.model.predict(X)
        return Cluster(predict[0]).name
