from importsearch import importsearch

def main():
    target_file = 'main.py'
    search = importsearch()
    search.search([target_file])

if __name__ == '__main__':
    main()
