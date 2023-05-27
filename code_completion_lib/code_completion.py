import pandas as pd
from math import *
import numpy as np
import json
import time
from pandas import DataFrame

from sklearn.neighbors import NearestCentroid
from sklearn.cluster import SpectralClustering, DBSCAN, MeanShift, estimate_bandwidth, AffinityPropagation, KMeans, \
    AgglomerativeClustering
from sklearn import metrics

import pickle
from operator import itemgetter
from code_completion_lib.necessary_functions import read_json, find_imported_methods

from thefuzz import fuzz


class CodeCompletion:
    model = None
    df = None

    def __init__(self, size: str, logger):
        self.logger = logger
        self.logger.set_name(__name__)
        self.size = size
        if size == 'small':
            self.df = pd.read_csv(r'code_completion_lib\imports\preprocessing_imports_small.csv')
        if size == 'medium':
            self.df = pd.read_csv(r'code_completion_lib\imports\preprocessing_imports_medium.csv')
        if size == 'big':
            self.df = pd.read_csv(r'code_completion_lib\imports\preprocessing_imports_big.csv')

    def get_variable_completion(self, model, variable_name: str, imports: list, number: int = 5):
        cluster_variable = read_json(rf'code_completion_lib/methods/models/{self.size}/prob/r_c_v_{model}.json')

        cluster_name = self.cluster_predict(imports, model=model)

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

    def get_default_function_completion(self, variable_name: str, number: int = 5):
        variable_method = read_json(rf'code_completion_lib/methods/models/{self.size}/prob/default.json')

        # result for plugin: list[suggestion considering the imports | class for this suggestion]
        result: list = []

        best_score = 0
        best_match = 'p'
        for variable in variable_method.keys():
            score = fuzz.WRatio(variable, variable_name)
            if score > best_score:
                best_score = score
                best_match = variable

        methods = variable_method[best_match]

        sorted_methods = dict(sorted(methods.items(), key=itemgetter(1)))
        keysList = list(sorted_methods.keys())
        keysList.reverse()

        return keysList[:number]


    def get_function_completion(self, model, variable_name: str, imports_lib: list = None, full_imports: list = None,
                                number: int = 5, cluster=None):
        model = model.replace(".csv", "")
        variable_method = read_json(rf'code_completion_lib/methods/models/{self.size}/prob/r_v_m_{model}.json')

        if cluster is None:
            cluster_name: str = self.cluster_predict(imports_lib, model)
        else:
            cluster_name: str = cluster

        # result for plugin: list[suggestion considering the imports | class for this suggestion]
        result: list = []

        best_score = 0
        best_match = 'p'
        for variable in variable_method.keys():
            score = fuzz.WRatio(variable, variable_name)
            if score > best_score:
                best_score = score
                best_match = variable

        if cluster_name in variable_method[best_match].keys():
            methods = variable_method[best_match][cluster_name]
        else:
            cluster_name = list(variable_method[best_match].keys())[0]
            methods = variable_method[best_match][cluster_name]

        sorted_methods = dict(sorted(methods.items(), key=itemgetter(1)))
        keysList = list(sorted_methods.keys())
        keysList.reverse()
        if imports_lib is None:
            return keysList[:number]

        imports = []
        for element in full_imports:
            imports.append(element.split("|"))

        imported_methods = find_imported_methods(sorted_methods, imports)
        for key in imported_methods.keys():
            if key[0] == key[1]:
                result.append(f"{key[1]}| ")
            else:
                result.append(f"{key[1]}|{key[0].replace(f'.{key[1]}', ' ')}")

        result.reverse()

        return result[:number]

    def relations_variable_with_method(self, X: DataFrame, y: DataFrame, model: str):
        model = model.replace(".csv", "")
        df = X.copy()

        df.insert(1, 'method', y['method'])
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
        with open(f'code_completion_lib/methods/models/{self.size}/prob/r_v_m_{model}.json', 'w',
                  encoding='utf-8') as f:
            json.dump(variable_method, f, ensure_ascii=False, indent=4)

    def default_task(self, X: DataFrame, y: DataFrame):
        df = X[["varible_name"]].copy()

        df.insert(1, 'method', y['method'])
        variable_method: dict = {}

        # Adding variables
        for line in df.values:
            variable_method[line[0]] = {}

        # Adding methods with their frequency
        for line in df.values:
            if line[1] in variable_method[line[0]].keys():
                variable_method[line[0]][line[1]] += 1
            else:
                variable_method[line[0]][line[1]] = 1

        # Calculating the probability
        for method in variable_method.values():

            total = 0
            for name, value in method.items():
                total += value

            for name, value in method.items():
                method[name] /= total
        with open(f'code_completion_lib/methods/models/{self.size}/prob/default.json', 'w',
                  encoding='utf-8') as f:
            json.dump(variable_method, f, ensure_ascii=False, indent=4)

    def relations_cluster_with_variable(self, X: DataFrame, y: DataFrame, model):
        model = model.replace(".csv", "")
        df = X.copy()
        df.insert(1, 'method', y['method'])
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

        with open(f'code_completion_lib/methods/models/{self.size}/prob/r_c_v_{model}.json', 'w',
                  encoding='utf-8') as f:
            json.dump(cluster_variable, f, ensure_ascii=False, indent=4)

    def import_clusterization(self):

        with open(r"analysis\imports\import_clusterization_" + self.size + ".txt", "w") as file:
            file.write("---------------------------------------------------------------------------\n")

        # cluster_model = AgglomerativeClustering(n_clusters=13, affinity='euclidean', linkage='ward')
        # cluster_model = DBSCAN(eps=0.1, min_samples=150)
        # cluster_model = SpectralClustering(n_clusters=13, assign_labels='discretize', random_state=0)
        # cluster_model = MeanShift()
        # cluster_model = AffinityPropagation(random_state=5)

        self.logger.info(f"size = {self.size}")

        models = [MeanShift(bandwidth=2.3),
                  SpectralClustering(n_clusters=13, assign_labels='discretize', random_state=0),
                  AgglomerativeClustering(n_clusters=13, metric='euclidean', linkage='ward'),
                  KMeans(n_clusters=13, random_state=0, n_init="auto"),
                  AffinityPropagation(damping=0.999, random_state=0)]
        for model in models:
            start = time.time()
            self.logger.info(f"model = {model}")

            # List for saving as .txt file
            result = []
            df = self.df.iloc[:, 1:]
            X = df.values[:, 1:]

            result.append(f"{len(df)} notebooks")

            tmp = df.copy()

            centroids_result = []
            cluster_model = model

            y_predict = cluster_model.fit_predict(X)
            labels = cluster_model.labels_

            end = time.time() - start
            result.append(model)
            result.append(f"Clustering time: {end}")

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
            pickle.dump(clf, open(rf"code_completion_lib\models\{self.size}\{model}", 'wb'))

            start = time.time()
            self.cluster_predict(["numpy", "sklearn", "matplotlib", "pandas"], model)
            end = time.time() - start
            result.append(f"Prediction time: {end}")

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
                    f"{notebook[0]} {(15 - len(notebook[0])) * ' '} {notebook[1]} {(20 - len(f'{notebook[1]}')) * ' '} Cluster_{j} {(45 - len(f'Cluster_{j}')) * ' '} {imports}")
                j += 1

            with open(r"analysis\imports\import_clusterization_" + self.size + ".txt", "a") as file:
                for line in result:
                    file.write(f"{line}\n")

            self.logger.info('Clusterization ended')

    def load_clusterization_model(self, filename):
        self.model = pickle.load(open(filename, 'rb'))

    def cluster_predict(self, imports: list, model) -> str:
        """Predict cluster for one notebook by imports"""

        self.load_clusterization_model(rf"code_completion_lib\models\{self.size}\{model}")

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
        return f"CLUSTER_{predict[0]}"
