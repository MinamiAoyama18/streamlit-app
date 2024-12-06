import sys
print("Python path:")
print('\n'.join(sys.path))
print("\nTrying imports:")
import plotly
import plotly.express
print("Plotly version:", plotly.__version__)
print("Plotly location:", plotly.__file__) 

