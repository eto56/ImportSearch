
        
def print_tree(tree, node, indent="|-", visited=None):

    tree = edit_map(tree)
    if tree is None:
        return
    
    if visited is None:
        visited = set()
    if node in visited:
        print(indent + f"{node}")
        return
    visited.add(node)
    print(indent + node)
    for child in tree.get(node, []):
        print_tree(tree, child, "  "+indent, visited)

def edit_map(map):

    map_index = set()
    for key in map:
        map_index.add(key)
    
    for key in map:
        for value in map[key]:
            pyf = value + '.py'
            if pyf in map_index:
                map[key].remove(value)
                map[key].append(pyf)
    return map



if __name__ == '__main__':
    sample_tree = {
        "main.py": ["utils.py", "config.py"],
        "utils.py": ["logger.py", "helpers.py"],
        "helpers.py": [],
        "config.py": ["helpers.py"],
        "logger.py": []
    }
    print(edit_map(sample_tree))
    print("Dependency Tree:")
    print_tree(sample_tree, "main.py")



         
