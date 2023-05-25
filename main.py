from code_completion_lib.code_completion import CodeCompletion
from code_completion_lib.imports.imports import Imports
from code_completion_lib.parse_notebooks import Parser
from code_completion_lib.methods.find_methods_in_code import Methods

from code_completion_lib.logger.logger import Logger
import sklearn
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from thefuzz import fuzz as f

if __name__ == '__main__':
    logger = Logger(__name__, mode="a")
    logger.info("-----------------------------------------------------")
    path = "C:\data\data_parsed"
    try:

        #parcer = Parser(r'C:\test\notebooks', r'C:\test\data_parsed')
        #parcer.parse()
        #parcer.check_language()
        #
        #import_class = Imports(r'C:\data\data_parsed')
        #import_class.process()
        #
        #completion = CodeCompletion()
        #completion.import_clusterization()
        #
        model_path = rf'code_completion_lib\models\small'
        methods = Methods(os.path.join(path, "small"),size="small", logger=logger)
        methods.find_methods_test(model_path)
        #
        #completion.relations_variable_with_method()
        #completion.relations_cluster_with_variable()


    except Exception:
        logger.error("Exception")
