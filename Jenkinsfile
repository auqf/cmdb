pipeline {
  agent any
  stages {
    stage('checkout') {
      steps {
        git(changelog: true, poll: true, url: 'https://gitee.com/auqf12/cmdb.git', branch: 'master', credentialsId: 'ff066402-04a3-46e6-b58a-7f89de35448f')
      }
    }

  }
}