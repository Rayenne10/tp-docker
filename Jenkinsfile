// Job "Pipeline from SCM", branche */main, Script Path Jenkinsfile.
// Agent Linux dedie : Python 3 + venv, Git, Docker CLI et daemon accessibles.
pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
    }
    triggers { githubPush() }
    environment {
        IMAGE_NAME = 'counter-app'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.LOCAL_IMAGE = "counter-app:ci-${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(12)}"
                }
            }
        }
        stage('Build application') {
            steps {
                sh '''python3 -m venv .venv
                    .venv/bin/pip install -r requirements-dev.txt
                    .venv/bin/python -m compileall -q app.py
                '''
            }
        }
        stage('Unit tests') {
            steps { sh '.venv/bin/python -m pytest --junitxml=reports/junit.xml' }
            post { always { junit 'reports/junit.xml' } }
        }
        stage('Build image') {
            when { expression { env.BRANCH_NAME == 'main' || env.GIT_BRANCH in ['main', 'origin/main'] } }
            steps { sh 'docker build --pull -t "$LOCAL_IMAGE" .' }
        }
        stage('Publish Docker Hub') {
            when { expression { env.BRANCH_NAME == 'main' || env.GIT_BRANCH in ['main', 'origin/main'] } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USR', passwordVariable: 'DOCKERHUB_TOKEN')]) {
                    // Token dans le shell, jamais dans une interpolation Groovy.
                    // Configuration Docker temporaire isolee, supprimee meme si push echoue.
                    sh '''set +x
                        export DOCKER_CONFIG="$(mktemp -d)"
                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT
                        printf '%s' "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USR" --password-stdin
                        REMOTE_IMAGE="$DOCKERHUB_USR/$IMAGE_NAME"
                        TAG="${BUILD_NUMBER}-${GIT_COMMIT}"
                        trap 'docker image rm "$REMOTE_IMAGE:$TAG" "$REMOTE_IMAGE:latest" >/dev/null 2>&1 || true; rm -rf "$DOCKER_CONFIG"' EXIT
                        docker tag "$LOCAL_IMAGE" "$REMOTE_IMAGE:$TAG"
                        docker tag "$LOCAL_IMAGE" "$REMOTE_IMAGE:latest"
                        docker push "$REMOTE_IMAGE:$TAG"
                        docker push "$REMOTE_IMAGE:latest"
                    '''
                }
            }
        }
    }
    post {
        always {
            script {
                if (env.LOCAL_IMAGE) {
                    sh 'docker image rm "$LOCAL_IMAGE" >/dev/null 2>&1 || true'
                }
            }
            deleteDir()
        }
        success { echo 'Etapes executees avec succes ; consulter Publish Docker Hub pour la publication.' }
    }
}
