# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import PrimitiveProtocol_pb2 as PrimitiveProtocol__pb2


class CmdExecutorStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateWorkspace = channel.unary_unary(
                '/CmdExecutor/CreateWorkspace',
                request_serializer=PrimitiveProtocol__pb2.WorkspaceParamRequest.SerializeToString,
                response_deserializer=PrimitiveProtocol__pb2.WorkspacePathReply.FromString,
                )


class CmdExecutorServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CreateWorkspace(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CmdExecutorServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateWorkspace': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateWorkspace,
                    request_deserializer=PrimitiveProtocol__pb2.WorkspaceParamRequest.FromString,
                    response_serializer=PrimitiveProtocol__pb2.WorkspacePathReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'CmdExecutor', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class CmdExecutor(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CreateWorkspace(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/CmdExecutor/CreateWorkspace',
            PrimitiveProtocol__pb2.WorkspaceParamRequest.SerializeToString,
            PrimitiveProtocol__pb2.WorkspacePathReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
