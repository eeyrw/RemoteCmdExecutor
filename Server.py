from concurrent import futures
import grpc
import PrimitiveProtocol_pb2
import PrimitiveProtocol_pb2_grpc
import os
import shutil
import subprocess


class CmdExecutorServicer(PrimitiveProtocol_pb2_grpc.CmdExecutor):
    def __init__(self):
        self.tempDir = './temp'
        self.createDir(self.tempDir)

    def CreateWorkspace(self, request, context):
        result = False
        print("CreateWorkspace function called")
        dirName = request.name
        dirSpecificPath = request.specificPath
        if dirSpecificPath is not '':
            finalDir = os.path.join(self.tempDir, dirSpecificPath)
        else:
            finalDir = os.path.join(self.tempDir, dirName)

        try:
            self.overwriteDir(finalDir)
            result = True
        except Exception as e:
            print(e)
        finally:
            relDir = os.path.relpath(finalDir, self.tempDir)
            return PrimitiveProtocol_pb2.WorkspacePathReply(
                path=relDir,
                isSuccessful=result
            )

    def DeleteWorkspace(self, request, context):
        result = False
        print("DeleteWorkspace function called")
        dirName = request.name
        dirSpecificPath = request.specificPath
        if dirSpecificPath is not '':
            finalDir = os.path.join(self.tempDir, dirSpecificPath)
        else:
            finalDir = os.path.join(self.tempDir, dirName)

        try:
            shutil.rmtree(finalDir)
            result = True
        except Exception as e:
            print(e)
        finally:
            relDir = os.path.relpath(finalDir, self.tempDir)
            return PrimitiveProtocol_pb2.WorkspacePathReply(
                path=relDir,
                isSuccessful=result
            )

    def UploadFile(self, request, context):
        result = False
        filePath = request.path
        fileContent = request.fileContent
        finalDir = os.path.join(self.tempDir, filePath)
        try:
            self.overwriteDir(os.path.dirname(finalDir))
            with open(finalDir, 'wb') as f:
                f.write(fileContent)
            result = True
        except Exception as e:
            print(e)
        finally:
            relDir = os.path.relpath(finalDir, self.tempDir)
            return PrimitiveProtocol_pb2.WorkspacePathReply(
                path=relDir,
                isSuccessful=result
            )

    def DownloadFile(self, request, context):
        result = False
        fileContent = bytearray()
        filePath = request.path
        finalDir = os.path.join(self.tempDir, filePath)
        try:
            with open(finalDir, 'rb') as f:
                fileContent = f.read()
            result = True
        except Exception as e:
            print(e)
        finally:
            relDir = os.path.relpath(finalDir, self.tempDir)
            return PrimitiveProtocol_pb2.FileDownloadReply(
                path=relDir,
                isSuccessful=result,
                fileContent=fileContent
            )

    def RunCmd(self, request, context):
        returnCode = 1
        out = ''.encode('utf8')
        err = ''.encode('utf8')
        finalCurrentDir = os.path.join(self.tempDir, request.currentDir)
        try:
            proc = subprocess.Popen(
                request.cmdString,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=finalCurrentDir
            )
            out, err = proc.communicate()
            returnCode = proc.returncode
        except Exception as e:
            print(e)
        finally:
            return PrimitiveProtocol_pb2.CmdResultReply(
                returnCode=returnCode,
                stdout=out,
                stderr=err
            )

    def overwriteDir(self, dir):
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)

    def createDir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)


def serve():
    MAX_MESSAGE_LENGTH = 100*1024*1024
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5), options=[(
        'grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)])
    PrimitiveProtocol_pb2_grpc.add_CmdExecutorServicer_to_server(
        CmdExecutorServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("grpc server start...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
