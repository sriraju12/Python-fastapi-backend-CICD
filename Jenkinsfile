pipeline {
    agent any
    environment {
        SCANNER_HOME = tool 'sonar-scanner'
        DOCKER_IMAGE = "sriraju12/backend-app:${BUILD_NUMBER}"
    }
    stages {
        stage ("Clean workspace") {
            steps {
                cleanWs()
            }
        }
        stage ("Git checkout") {
            steps {
                git branch: 'main', url: 'https://github.com/sriraju12/Python-fastapi-backend-CICD.git'
            }
        }

        stage('Build Application') {
            steps {
                script {
                    sh 'python3 -m venv venv'

                    sh '''
                    bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
                    '''
                }
            }
        }
        
        stage("SonarQube Analysis") {
            steps {
                withSonarQubeEnv('sonar-server') {
                    sh ''' $SCANNER_HOME/bin/sonar-scanner -Dsonar.projectName=python-app \
                    -Dsonar.projectKey=python-app '''
                }
            }
        }
        stage("Quality Gate") {
            steps {
                script {
                    waitForQualityGate abortPipeline: true, credentialsId: 'sonar-secret'
                }
            }
        }
        stage ("Trivy File Scan") {
            steps {
                sh "trivy fs --format table -o trivy-fs-report.html ."
            }
        }
       stage('Build and Push Docker Image') {
         environment {
            REGISTRY_CREDENTIALS = credentials('dockerhub-secret')
      }
      steps {
        script {
            sh 'docker context use default'  
            sh "docker build -t ${DOCKER_IMAGE} ."
            def dockerImage = docker.image("${DOCKER_IMAGE}")
            docker.withRegistry('https://index.docker.io/v1/', "dockerhub-secret") {
                dockerImage.push()
            }
        }
      }
    }
    stage('Docker Image Scan') {
       steps {
           sh "trivy image --format table -o trivy-image-report.html ${DOCKER_IMAGE}"
           }
        }
}
       
}

