from concurrent import futures
import grpc
import PrimitiveProtocol_pb2
import PrimitiveProtocol_pb2_grpc




class CmdExecutorServicer(PrimitiveProtocol_pb2_grpc.CmdExecutor):
    def CreateWorkspace(self, request, context):
        print("CreateWorkspace function called")
        return PrimitiveProtocol_pb2.WorkspacePathReply(
            path='',
            isSuccessful=False
        )

    

def serve():
    MAX_MESSAGE_LENGTH = 100*1024*1024
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5), options=[(
        'grpc.max_send_message_length', MAX_MESSAGE_LENGTH), ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)])
    PrimitiveProtocol_pb2_grpc.add_CmdExecutorServicer_to_server(
        CmdExecutorServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("grpc server start...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
