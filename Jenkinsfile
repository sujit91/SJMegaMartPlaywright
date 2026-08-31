pipeline {
  agent any
  options {
    timestamps()
    disableConcurrentBuilds()
  }
  environment {
    BASE_URL = 'https://sujitjena90.github.io/SujitTestingAutomation/'
    HEADLESS = 'true'
    PYTHONUNBUFFERED = '1'
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Setup Python') {
      steps {
        bat '''
          python -m venv .venv
          .venv\\Scripts\\python -m pip install --upgrade pip
          .venv\\Scripts\\pip install -r requirements.txt
          .venv\\Scripts\\playwright install chromium
        '''
      }
    }
    stage('Smoke') {
      steps {
        bat '.venv\\Scripts\\pytest tests -m smoke --browser chromium --junitxml=reports/smoke-junit.xml --html=reports/smoke.html --self-contained-html'
      }
    }
    stage('Regression') {
      steps {
        bat '.venv\\Scripts\\pytest tests --browser chromium --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html'
      }
    }
  }
  post {
    always {
      junit allowEmptyResults: true, testResults: 'reports/*junit.xml'
      publishHTML(target: [
        reportDir: 'reports',
        reportFiles: 'report.html',
        reportName: 'Playwright HTML Report',
        keepAll: true,
        alwaysLinkToLastBuild: true
      ])
      archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
    }
  }
}
