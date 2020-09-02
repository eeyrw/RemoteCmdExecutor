import PrimitiveProtocol_pb2
import PrimitiveProtocol_pb2_grpc
import grpc
import random
import os


class RemoteFile:
    def __init__(self, client, remoteWorkspace):
        self.fileInfoDict = {}
        self.remoteWorkSpace = remoteWorkspace
        self.client = client

    def addLocalFile(self, name, filePath):
        remoteFileName = os.path.normpath(
            filePath).replace('\\', '_').replace('/', '_')
        self.fileInfoDict[name] = ('UPLOAD', filePath, remoteFileName)
        print(remoteFileName)

    def addRemoteFile(self, name, filePath):
        remoteFileName = os.path.normpath(
            filePath).replace('\\', '_').replace('/', '_')
        print(remoteFileName)
        self.fileInfoDict[name] = ('DOWNLOAD', filePath, remoteFileName)

    def upload(self):
        for _, (fileType, fileLocalPath, remoteFileName) in self.fileInfoDict.items():
            if fileType == 'UPLOAD':
                self.client.uploadFile(os.path.join(
                    self.remoteWorkSpace, remoteFileName), fileLocalPath)

    def download(self):
        for _, (fileType, fileLocalPath, remoteFileName) in self.fileInfoDict.items():
            if fileType == 'DOWNLOAD':
                self.client.downloadFile(os.path.join(
                    self.remoteWorkSpace, remoteFileName), fileLocalPath)

    def getRemotePath(self, indentifier):
        return self.fileInfoDict[indentifier][2]


class RemoteMethod:
    def __init__(self, remoteAddress='localhost'):
        self.channel = grpc.insecure_channel(
            '%s:50051' % remoteAddress)  # 连接上gRPC服务端
        self.stub = PrimitiveProtocol_pb2_grpc.CmdExecutorStub(self.channel)

    def createWorkspace(self, name):
        response = self.stub.CreateWorkspace(
            PrimitiveProtocol_pb2.WorkspaceParamRequest(name=name)
        )
        return response.isSuccessful

    def deleteWorkspace(self, name):
        response = self.stub.DeleteWorkspace(
            PrimitiveProtocol_pb2.WorkspaceParamRequest(name=name)
        )
        return response.isSuccessful

    def uploadFile(self, remotePath, localPath):
        with open(localPath, 'rb') as f:
            fileContent = f.read()
        response = self.stub.UploadFile(
            PrimitiveProtocol_pb2.FileUploadRequest(
                path=remotePath,
                fileContent=fileContent
            )
        )
        return response.isSuccessful

    def downloadFile(self, remotePath, localPath):
        response = self.stub.DownloadFile(
            PrimitiveProtocol_pb2.FileDownloadRequest(
                path=remotePath
            )
        )
        self.createDir(os.path.dirname(localPath))
        with open(localPath, 'wb') as f:
            f.write(response.fileContent)

        return response.isSuccessful

    def runCmd(self, cmdString, currentDir='.'):
        response = self.stub.RunCmd(
            PrimitiveProtocol_pb2.RunCmdRequest(
                cmdString=cmdString,
                currentDir=currentDir
            )
        )
        print('=====Remote Stdout=======')
        print(response.stdout.decode('gbk'))
        print('=====Remote Stderr=======')
        print(response.stderr.decode('gbk'))

    def createDir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)


if __name__ == "__main__":
    remoteMethod = RemoteMethod()
    print(remoteMethod.createWorkspace('Test_R'))
    rf = RemoteFile(remoteMethod, 'Test_R')
    rf.addLocalFile('localF', './Client.py')
    rf.addRemoteFile('remoteF', './Client_FromRemote.py')
    rf.upload()
    remoteMethod.runCmd('copy %s %s' % (rf.getRemotePath(
        'localF'), rf.getRemotePath('remoteF')), currentDir='Test_R')
    rf.download()
    remoteMethod.deleteWorkspace('Test_R')
