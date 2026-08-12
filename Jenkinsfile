pipeline {
    agent any

    environment {
        EC2_IP = '3.110.194.212'
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
                set -e
                timeout 60 ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_IP} "
                    set -e
                    if [ ! -d ${APP_DIR} ]; then
                        git clone https://github.com/IrfanPasha05/pypulse.git ${APP_DIR}
                    fi
                    cd ${APP_DIR}
                    git pull origin main
                    source venv/bin/activate
                    pip install -r requirements.txt
                    sudo systemctl restart pypulse
                "
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