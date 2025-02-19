from importsearch import importsearch

def main():
    target_file = 'sample_dir/main.py'
    search = importsearch(target_file,debug = True)
    search.search()

if __name__ == '__main__':
    main()
