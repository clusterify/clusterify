import helper

test_modules = ['fetchers', 'urinorm']

def getTestCases():
    tests = []
    for module_name in test_modules:
        module = __import__('urljr.test.test_' + module_name, {}, {}, [None])
        tests.append(helper.getTestSuite(module))
    return tests

if __name__ == '__main__':
    helper.runAsMain()
