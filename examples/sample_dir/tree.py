class make_tree():

    def __init__(self,dir_map):

        self.dir_map = dir_map
        self.visited = set()
        
    
    def draw_tree(self,dir_map):
        #print('Drawing tree')
        for key in dir_map:
            print(key)
            self.draw_tree(dir_map[key])
        
def print_tree(tree, node, indent="", visited=None):
    if visited is None:
        visited = set()
    # 循環参照を防止するため、すでに訪れたノードはスキップ
    if node in visited:
        print(indent + f"{node} (already visited)")
        return
    visited.add(node)
    print(indent + node)
    # 現在のノードが子ノードを持つ場合
    for child in tree.get(node, []):
        print_tree(tree, child, indent + "  ", visited)

# 例: あなたのライブラリの dfs_search によって得られる summary_map を利用
if __name__ == '__main__':
    # 仮に、summary_map が各ファイルからその import されたファイルのリストを持つ辞書であるとします。
    sample_tree = {
        "main.py": ["utils.py", "config.py"],
        "utils.py": ["logger.py", "helpers.py"],
        "helpers.py": [],
        "config.py": ["helpers.py"],
        "logger.py": []
    }
    
    print("Dependency Tree:")
    print_tree(sample_tree, "main.py")



         