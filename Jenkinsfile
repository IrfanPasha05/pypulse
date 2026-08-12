pipeline {
    agent any

    environment {
        EC2_IP = '3.110.194.212'   // replace with your actual IP
        EC2_USER = 'ubuntu'
        APP_DIR = '/home/ubuntu/pypulse'
    }

    stages {
        stage('Build') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest
                '''
            }
        }

        stage('Deploy') {
            steps {
                sshagent(credentials: ['pypulse-ec2-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_IP} '
                            cd ${APP_DIR} &&
                            git pull origin main &&
                            source venv/bin/activate &&
                            pip install -r requirements.txt &&
                            pkill gunicorn || true &&
                            nohup gunicorn --bind 0.0.0.0:5000 app:app > gunicorn.log 2>&1 &
                        '
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'PyPulse deployed successfully!'
        }
        failure {
            echo 'Pipeline failed — check the stage logs above.'
        }
    }
}