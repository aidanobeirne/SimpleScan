from setuptools import setup, find_packages

setup(
   name='LightWork',
   version='1.0',
   description='Generalized code to run high-dimensional data scans using optics instrumentation',
   author='Aidan OBeirne',
   author_email='aidanobeirne@me.com',
   url='https://github.com/aidanobeirne/LightWork.git',
   packages=find_packages(),  #same as name
   include_package_data=True,
   # package_data={'Andor dll': ['ParentClasses/Andor/*.dll'], 'Thorlabs dll': ['ParentClasses/Andor/ThorlabsStages/*.dll'], 'Thorlabs lib': ['ParentClasses/Andor/ThorlabsStages/*.lib'],
   # 'Thorlabs h': ['ParentClasses/Andor/ThorlabsStages/*.h'], 'Thorlabs xml': ['ParentClasses/Andor/ThorlabsStages/*.xml']},
   # package_data={'dlls': ['ParentClasses/Andor/*.dll'], 'examples' : ['ExperimentExamples/*.py']},
   zip_safe=False,
   install_requires=['PyMeasure', 'PyVISA'], #external packages as dependencies
)