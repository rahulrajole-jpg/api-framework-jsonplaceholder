pipeline {
    agent any

    triggers {
        cron('H/2 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    PYTHONUNBUFFERED=1 pytest -s -v --maxfail=1 --disable-warnings --alluredir=allure-results -n auto
                '''
            }
        }

        stage('Allure Report') {
            steps {
                sh '/opt/homebrew/bin/allure generate allure-results --clean -o allure-report'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'allure-report/**', fingerprint: true
        }
    }
}
