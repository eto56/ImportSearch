import ast
import os
 



class importsearch:
    def __init__(self):
        self.visited = set()
        self.summary_map = {}


    def extract_imports(self, filename):

        # get "import" and "from ... import" statements from a python file

        if not os.path.exists(filename):
            #print('No such file')
            return []
        
        if not filename.endswith('.py'):
            filename += '.py'
        #print('Extracting imports from ' + filename)
        with open(filename, 'r') as f:
            tree = ast.parse(f.read(), filename)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        #print(filename + ' imports: ' + str(imports))
        return imports


    def get_next_file(self,filename_list):
        # yolo.model -> yolo/model

        module_list = filename_list.copy()
        path_list = []
        for module in module_list:
            filename_split = module.split('.')
            path = os.path.join(*filename_split)
            
            path_list.append(path)
        
        return path_list

    def dfs_search(self,filename_list):
        # Depth First Search
        # filename_list: list of filenames
        # visited: set of visited filenames
        # graph: dictionary of filename -> list of filenames

        for filename in filename_list:
            if filename in self.visited:
                continue
            self.visited.add(filename)

            if not filename.endswith('.py'):
                    filename += '.py'
            next_files = self.get_next_file(self.extract_imports(filename))
            if next_files==[]:
                continue

            self.summary_map[filename] = next_files
            
            

            self.dfs_search(next_files)


    def summary(self):
        for key in  self.summary_map.keys():

            print ('File: ' + key)
            print(str( self.summary_map[key]))
            print ('-----------------------')

        
        print ('Visited files: ' + str(self.visited))
    
    def search(self, filename_list):
        self.dfs_search(filename_list)
        self.summary()
        

         


if __name__ == '__main__':
    
    target_file = 'main.py'

    search = importsearch()

    search.search([target_file])


 

 
        

