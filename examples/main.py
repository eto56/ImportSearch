# examples/main.py

import importsearch

def main():
    target_file = 'main.py'
    search = importsearch.importsearch()
    search.search([target_file])

if __name__ == '__main__':
    main()
