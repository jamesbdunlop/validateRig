:: This batch file runs the unitests with coverage and generates the html for checking in browser

set PYTHONPATH=%PYTHONPATH%;T:\software\validateRig

coverage run --omit T:\software\validateRig\core\mayaValidation.py -m unittest test_api.py
coverage run --append --omit T:\software\validateRig\core\mayaValidation.py -m unittest test_validator.py
coverage run --append --omit T:\software\validateRig\core\mayaValidation.py -m unittest test_nodes.py
coverage run --append --omit T:\software\validateRig\core\mayaValidation.py -m unittest test_parser.py
coverage html -i
coverage report -i
