import ast
import os

from tree import print_tree  



class importsearch:
    def __init__(self,filename=''):
        self.visited = set()
        self.summary_map = {}
        self.init_file = ''
        self.chdir(filename)

    def pre_dir(self,filename):
        # get the previous directory
        return os.path.dirname(filename)
    
    
    def chdir(self,filename):

        # change directory to the directory of the target file
        if not os.path.exists(filename):
            return
        if os.path.isdir(filename):
            os.chdir(filename)
        else:
            os.chdir(os.path.dirname(filename))
        self.init_file = self.get_script_name(filename)
        #print('Initial file: ' + self.init_file)


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
        #print("dir",filename_list)
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
        #print(filename_list)
        for filename in filename_list:
            if filename in self.visited:
                continue
            self.visited.add(filename)

            if not filename.endswith('.py'):
                    filename += '.py'
            next_files = self.get_next_file(self.extract_imports(filename))

           
            
            #print (filename,next_files)
            if next_files==[]:
                continue

            self.summary_map[filename] = next_files
            
            

            self.dfs_search(next_files)


    def summary(self):
        self.summary_map = self.edit_map(self.summary_map)
        for key in  self.summary_map.keys():
            print ()
            print ('File: ' + key)
            print(str( self.summary_map[key]))
            print ()
            print ('-----------------------')
         

        print ()
        print ('Visited files: ' + str(self.visited))
        print ()
        print ('-----------------------')
        print ('import tree')
        print ()
        print_tree(self.summary_map,self.init_file)
        
        
    def edit_map(self,map):

        map_index = set()
        for key in map:
            map_index.add(key)
        
        for key in map:
            for value in map[key]:
                pyf = value + '.py'
                if pyf in map_index:
                    # add .py to the value
                    

                    map[key].remove(value)
                    map[key].append(pyf)
        return map

         
    
    def search(self):
        self.dfs_search([self.init_file])
        self.summary()


    def get_script_name(self,filename):
        return os.path.basename(filename)
    

def search (filename):
    search = importsearch(filename)
    search.search()
    
     
if __name__ == '__main__':
    
    target_file = '../../examples/sample_dir/main.py'

    search(target_file)

 

 
        

