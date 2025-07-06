'''
the setup.py file is an essential part of packaging and distributing Python projects 
It is used by setuptools (or distutils in older python versions ) to define the configuration of our projects , such as metadata,dependencies,and more

findpackages is going to scan through all these folders finding __init__.py file , its going to consider that particular folder as a package
setup is responsible for providing all information regarding projects over here

Without List: feature_names = ['age', 'income', 'education']

Problem: Someone might accidentally put a number here later.

With List: feature_names: List[str] = ['age', 'income', 'education']

Benefit: Clearly states "this list should only contain text (strings)." If you try to add a number like feature_names.append(123), your code editor will warn you before you even run it.
Without List: predictions = model.predict(test_data)

Problem: What kind of predictions? Individual scores? A list of scores?

With List: predictions: List[float] = model.predict(test_data)

Benefit: Makes it clear: "This variable predictions will hold a list of decimal numbers (the prediction scores)."
Without List: file_paths = get_data_files()

Problem: Are these file paths strings? Or something else?

With List: file_paths: List[str] = get_data_files()

Benefit: "This file_paths variable is a list, and every item in it is a text string (a file path)."
Storing Hyperparameters (e.g., learning rates for an experiment):

Without List: learning_rates = [0.01, 0.001, 0.0001]

With List: learning_rates: List[float] = [0.01, 0.001, 0.0001]
Benefit: Ensures that all learning rates in this list are decimal numbers.

In short, List (from typing) is like putting a clear label on your lists, telling everyone (including your code editor) exactly what kind of stuff is supposed to be inside that list. This helps catch mistakes early and makes your code much easier for others (and your future self) to understand.
'''
from setuptools import find_packages,setup
from typing import List

def get_requirements()->List[str]:
    '''
    this fn will return list of requirements

    '''
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
            # Real lines from file 
            lines=file.readlines()
            ## process each lines
            for line in lines:
                requirement=line.strip()
                ## ignore empty lines and e.
                if requirement and requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("Requirememnts.txt not found")

    return requirement_lst

setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Kafil aslam",
    author_email="Aslamkafil13@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
    )
## -e . is nothing but refering to setup.py file
