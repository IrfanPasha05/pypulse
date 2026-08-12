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
                    cd ${APP_DIR} &&
                    git pull origin main &&
                    python3 -m venv venv &&
                    source venv/bin/activate &&
                    pip install -r requirements.txt &&
                    pkill gunicorn || true &&
                    sleep 1 &&
                    setsid nohup venv/bin/gunicorn --bind 0.0.0.0:5000 app:app > gunicorn.log 2>&1 < /dev/null &
                    exit 0
                "
            '''
        }
    }
}