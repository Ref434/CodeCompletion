from code_completion_lib.code_completion import CodeCompletion
from code_completion_lib.imports.imports import Imports
from code_completion_lib.parse_notebooks import Parser
from code_completion_lib.methods.find_methods_in_code import Methods
import sys
import os

if __name__ == '__main__':

    print('Processing...')

    #parcer = Parser(r'C:\data\notebooks', r'C:\data\data_parsed')
    #parcer.parse()
    #parcer.check_language()

    #import_class = Imports(r'C:\data\data_parsed')
    #import_class.process()

    #completion = CodeCompletion()
    #completion.import_clusterization()


    #methods = Methods()
    #methods.find_methods(r'C:\data\data_parsed', r"code_completion_lib\methods\libraries\sklearn.json", 'sklearn.')

    #completion.relations_variable_with_method()
    #completion.relations_cluster_with_variable()

    print('END.')
