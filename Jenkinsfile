pipeline {
    agent any
    triggers {
        cron('H/2 * * * *') // Runs every 2 minutes (change to H */2 * * * for every 2 hours)
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                sh '. venv/bin/activate && pytest --maxfail=1 --disable-warnings --alluredir=allure-results -n auto'
            }
        }
        stage('Allure Report') {
            steps {
                sh '/opt/homebrew/bin/allure generate allure-results --clean -o allure-report'
                sh '/opt/homebrew/bin/allure open allure-report &'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'allure-report/**', fingerprint: true
        }
    }
}