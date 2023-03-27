from code_completion_lib.code_completion import CodeCompletion
from code_completion_lib.imports.imports import Imports
from code_completion_lib.parse_notebooks import Parser
from code_completion_lib.methods.find_methods_in_code import Methods

from code_completion_lib.logger.logger import Logger

if __name__ == '__main__':
    logger = Logger(__name__)

    try:

        parcer = Parser(r'C:\test\notebooks', r'C:\test\data_parsed')
        parcer.parse()
        parcer.check_language()

        import_class = Imports(r'C:\test\data_parsed')
        import_class.process()

        completion = CodeCompletion()
        completion.import_clusterization()

        methods = Methods()

        methods.find_methods(r'C:\test\data_parsed')

        completion.relations_variable_with_method()
        completion.relations_cluster_with_variable()

    except Exception:
        logger.error("Exception")
