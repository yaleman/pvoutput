pipeline {
    agent none
    stages {
        stage ('Test') {
            agent any
            steps {
                sh "pipenv install --dev && pipenv run pytest"
            }
        }
        stage ('Build') {
            agent any
            steps {
                sh "pip install pipenv"
                sh "pipenv install --dev && pipenv run python setup.py sdist bdist_wheel"
            }
        }
    }
}