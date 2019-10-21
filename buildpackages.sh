rm dist/*
pipenv run python setup.py sdist bdist_wheel

cd docs
pipenv run make clean html json
cd ..