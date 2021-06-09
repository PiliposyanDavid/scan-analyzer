def deployEnv = "production"
def service = "pa-scan-analyzer"
def kubectl = "kubectl -n pa-api"
def branch = "master"

pipeline {
    environment {
        registry = "gcr.io/picsartgc/backend/${deployEnv}/"
        service = "${service}"
    }

    parameters {
        string defaultValue: "master", description: 'Branch Name', name: 'branch'
        booleanParam(name: 'DEPLOY', defaultValue: true, description: 'Check To deploy it on Kubernetes')
    }
    agent { label 'master' }

    stages {
        stage("Code Pull") {
            steps {
                git branch: "${branch}",
                        credentialsId: '3ddfc8fe-1989-4e82-8ad7-d6fb4f232578',
                        url: 'https://github.com/PicsArt/pa-collections-service.git'
            }
        }

        stage('Building And Push Api Image') {
            steps {
                script {
                    dir('server') {
                        dockerImage = docker.build(registry + service + ":${BUILD_NUMBER}", "--build-arg ENTRY_ARG=start-api --force-rm .")
                        docker.withRegistry('https://gcr.io', 'gcr:jenkins-GCR') {
                            dockerImage.push()
                            dockerImage.push('latest')
                        }
                    }
                }
            }
        }


        stage('Building And Push Consumer Image') {
            steps {
                script {
                    dir('server') {
                        dockerImage = docker.build(registry + consumer + ":${BUILD_NUMBER}", "--build-arg ENTRY_ARG=start-consumer --force-rm .")
                        docker.withRegistry('https://gcr.io', 'gcr:jenkins-GCR') {
                            dockerImage.push()
                            dockerImage.push('latest')
                        }
                    }
                }
            }
        }
        stage('Deploy Api') {
            when {
                expression { params.DEPLOY == true }
            }
            steps {
                    withKubeConfig([credentialsId: 'config-backend-prod']) {
                        echo "Deploying image"
                        sh "${kubectl} kustomize server/deployment/${deployEnv}/ | " +
                                'sed "/containers/,/resources/ s/:latest/:${BUILD_NUMBER}/g" | ' +
                                "${kubectl} apply -f -"
                        sleep 10
                    }

            }
        }


        stage('Deploy Consumer') {
            when {
                expression { params.DEPLOY == true }
            }
            steps {
                 withKubeConfig([credentialsId: 'config-backend-prod']) {
                        echo "Deploying image"
                        sh "${kubectl} kustomize server/consumer-deployment/${deployEnv}/ | " +
                                'sed "/containers/,/resources/ s/:latest/:${BUILD_NUMBER}/g" | ' +
                                "${kubectl} apply -f -"
                        sleep 10
                 }
            }
        }
    }
}
