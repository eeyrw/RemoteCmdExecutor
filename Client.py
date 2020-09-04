import PrimitiveProtocol_pb2
import PrimitiveProtocol_pb2_grpc
import grpc
import random
import os


class RemoteCmdExecutor:
    def __init__(self, workspaceName, remoteMethod):
        self.workspaceName = workspaceName
        self.fileInfoDict = {}
        self.remoteMethod = remoteMethod

    def run(self, cmdString):
        self.genFileParamDict()
        cmdString = cmdString.format(**self.fileParamDict)
        self.upload()
        self.remoteMethod.runCmd(cmdString, self.workspaceName)
        self.download()

    def genFileParamDict(self):
        self.fileParamDict = {k:v[2] for k,v in self.fileInfoDict.items()}

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
                self.remoteMethod.uploadFile(os.path.join(
                    self.workspaceName, remoteFileName), fileLocalPath)

    def download(self):
        for _, (fileType, fileLocalPath, remoteFileName) in self.fileInfoDict.items():
            if fileType == 'DOWNLOAD':
                self.remoteMethod.downloadFile(os.path.join(
                    self.workspaceName, remoteFileName), fileLocalPath)

    def getRemotePath(self, indentifier):
        return self.fileInfoDict[indentifier][2]


class RemoteWorkEnv:
    def __init__(self, workspaceName, address):
        self.workspaceName = workspaceName
        self.address = address
        self.remoteMethod = RemoteMethod(self.address)

    def __enter__(self):
        self.remoteMethod.createWorkspace(self.workspaceName)
        self.remoteCmdExecutor = RemoteCmdExecutor(
            self.workspaceName, self.remoteMethod)
        return self.remoteCmdExecutor

    def __exit__(self, type, value, traceback):
        if traceback is None:
            # No exception, so commit
            self.remoteMethod.deleteWorkspace(self.workspaceName)
        else:
            # Exception occurred, so rollback.
            print(traceback)
            # return False



class RemoteMethod:
    def __init__(self, remoteAddress='localhost'):
        self.channel = grpc.insecure_channel(
            '%s:50051' % remoteAddress,
        )  # 连接上gRPC服务端
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
            ))
        return response.isSuccessful

    def downloadFile(self, remotePath, localPath):
        response = self.stub.DownloadFile(
            PrimitiveProtocol_pb2.FileDownloadRequest(
                path=remotePath
            ))
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
    with RemoteWorkEnv('Test_R','localhost') as executor:
        executor.addLocalFile('localF', './Client.py')
        executor.addRemoteFile('remoteF', './Client_FromRemote.py')
        executor.run('copy {localF} {remoteF}')
