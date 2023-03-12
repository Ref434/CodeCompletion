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


class Cluster(Enum):
    STRUCTURED_DATA = 0                                    # 10200.txt: 0.7134112111564094: ['pandas']
    SCIENTIFIC_COMPUTING = 1                               # 10169.txt: 0.9013646838548341: ['numpy', 'pandas', 'scipy', 'matplotlib']
    REQUESTS = 2                                           # 10291.txt: 0.9830515802329461: ['bs4', 'requests', 'pandas']
    SCIKIT_LEARN = 3                                       # 1002.txt: 0.6398195086803348: ['pandas', 'sklearn', 'matplotlib', 'numpy', 'bat']
    SCIKIT_LEARN_VISUALIZATION = 4                         # 10025.txt: 0.6851218730597738: ['pandas', 'numpy', 'matplotlib', 'seaborn', 'sklearn']
    TENSOR_FLOW = 5                                        # 1007.txt: 0.8785669741980751: ['tensorflow', 'numpy', 'matplotlib']
    STRUCTURED_DATA_VISUALIZATION = 6                      # 10653.txt: 0.9039525606841712: ['pandas', 'matplotlib', 'numpy', 'os']
    NUMPY_VISUALIZATION = 7                                # 10015.txt: 0.5440463000814826: ['numpy', 'matplotlib']
    DEEP_NEURAL_NETWORKS = 8                               # 10435.txt: 0.7808124094070849: ['torch', 'torchvision', 'matplotlib', 'numpy']
    SCIKIT_LEARN_WITH_NATURAL_LANGUAGE_PROCESSING = 9      # 20928.txt: 0.9716857106504793: ['numpy', 'matplotlib', 'pandas', 're', 'nltk', 'sklearn']
    STRUCTURED_DATA_VISUALIZATION_2 = 10                   # 1005.txt: 0.5565579401559042: ['pandas', 'numpy', 'matplotlib']
    IPython = 11                                           # 1010.txt: 0.9232101651914889: ['IPython']
    CS771 = 12                                             # 12922.txt: 0.92916907379603: ['numpy', 'cs771', 'matplotlib', 'time', 'random']
    QUANTUM_COMPUTERS = 13                                 # 13602.txt: 0.7753231106615648: ['sys', 'numpy', 'qiskit', 'Qconfig']


class CodeCompletion:
    variables_methods = {}
    clusters_variables = {}
    model = None
    df = None

    def __init__(self):
        self.df = pd.read_csv(r'code_completion_lib\imports\preprocessing_imports.csv')

    def relations_variable_with_method(self):
        df = pd.read_csv(r'code_completion_lib/methods/methods.csv')

        # Adding variables
        for line in df.values:
            self.variables_methods[line[0]] = {}

        # Adding clusters
        for line in df.values:
            self.variables_methods[line[0]][line[2]] = {}

        # Adding methods with their frequency
        for line in df.values:
            if line[1] in self.variables_methods[line[0]][line[2]].keys():
                self.variables_methods[line[0]][line[2]][line[1]] += 1
            else:
                self.variables_methods[line[0]][line[2]][line[1]] = 1

        # Calculating the probability
        for cluster in self.variables_methods.values():

            for method in cluster.values():
                total = 0
                for name, value in method.items():
                    total += value

                for name, value in method.items():
                    method[name] /= total

        with open('code_completion_lib/methods/relations_variable_with_method.json', 'w', encoding='utf-8') as f:
            json.dump(self.variables_methods, f, ensure_ascii=False, indent=4)

    def relations_cluster_with_variable(self):
        df = pd.read_csv('code_completion_lib/methods/methods.csv')

        # Adding clusters
        for line in df.values:
            self.clusters_variables[line[2]] = {}

        # Adding variables with their frequency
        for line in df.values:
            if line[0] in self.clusters_variables[line[2]].keys():
                self.clusters_variables[line[2]][line[0]] += 1
            else:
                self.clusters_variables[line[2]][line[0]] = 1

        # Calculating the probability
        for variable in self.clusters_variables.values():
            total = 0
            for name, value in variable.items():
                total += value

            for name, value in variable.items():
                variable[name] /= total


        with open('code_completion_lib/methods/relations_cluster_with_variable.json', 'w', encoding='utf-8') as f:
            json.dump(self.clusters_variables, f, ensure_ascii=False, indent=4)

    def import_clusterization(self):

        # List for saving as .txt file
        result = []

        df = self.df.iloc[:, 1:]
        X = df.values[:, 1:]

        result.append(f"{len(df)} notebooks")

        tmp = df.copy()

        centroids_result = []

        cluster_model = AgglomerativeClustering(n_clusters=13, affinity='euclidean', linkage='ward')
        #cluster_model = DBSCAN(eps=0.1, min_samples=150)
        #cluster_model = SpectralClustering(n_clusters=20, assign_labels='discretize', random_state=0)
        #cluster_model = MeanShift()
        #cluster_model = AffinityPropagation(random_state=5)
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
            result.append(f"{notebook[0]} {(15 - len(notebook[0]))* ' '} {notebook[1]} {(20 - len(f'{notebook[1]}'))* ' '} {Cluster(j).name} {(45 - len(Cluster(j).name))* ' '} {imports}")
            j += 1

        with open(r"analysis/import_clusterization.txt", "w") as file:
            for line in result:
                file.write(f"{line}\n")

        print('Clusterization ended')


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
