# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import warnings

import grpc

import langrocks.common.models.tools_pb2 as tools__pb2

GRPC_GENERATED_VERSION = "1.65.1"
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = "1.66.0"
SCHEDULED_RELEASE_DATE = "August 6, 2024"
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower

    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f"The grpc package installed is at version {GRPC_VERSION},"
        + f" but the generated code in tools_pb2_grpc.py depends on"
        + f" grpcio>={GRPC_GENERATED_VERSION}."
        + f" Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}"
        + f" or downgrade your generated code using grpcio-tools<={GRPC_VERSION}."
        + f" This warning will become an error in {EXPECTED_ERROR_RELEASE},"
        + f" scheduled for release on {SCHEDULED_RELEASE_DATE}.",
        RuntimeWarning,
    )


class ToolsStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetWebBrowser = channel.stream_stream(
            "/Tools/GetWebBrowser",
            request_serializer=tools__pb2.WebBrowserRequest.SerializeToString,
            response_deserializer=tools__pb2.WebBrowserResponse.FromString,
            _registered_method=True,
        )
        self.GetFileConverter = channel.unary_unary(
            "/Tools/GetFileConverter",
            request_serializer=tools__pb2.FileConverterRequest.SerializeToString,
            response_deserializer=tools__pb2.FileConverterResponse.FromString,
            _registered_method=True,
        )
        self.GetCodeRunner = channel.stream_stream(
            "/Tools/GetCodeRunner",
            request_serializer=tools__pb2.CodeRunnerRequest.SerializeToString,
            response_deserializer=tools__pb2.CodeRunnerResponse.FromString,
            _registered_method=True,
        )


class ToolsServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetWebBrowser(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetFileConverter(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetCodeRunner(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_ToolsServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetWebBrowser": grpc.stream_stream_rpc_method_handler(
            servicer.GetWebBrowser,
            request_deserializer=tools__pb2.WebBrowserRequest.FromString,
            response_serializer=tools__pb2.WebBrowserResponse.SerializeToString,
        ),
        "GetFileConverter": grpc.unary_unary_rpc_method_handler(
            servicer.GetFileConverter,
            request_deserializer=tools__pb2.FileConverterRequest.FromString,
            response_serializer=tools__pb2.FileConverterResponse.SerializeToString,
        ),
        "GetCodeRunner": grpc.stream_stream_rpc_method_handler(
            servicer.GetCodeRunner,
            request_deserializer=tools__pb2.CodeRunnerRequest.FromString,
            response_serializer=tools__pb2.CodeRunnerResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler("Tools", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers("Tools", rpc_method_handlers)


# This class is part of an EXPERIMENTAL API.
class Tools(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetWebBrowser(
        request_iterator,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            "/Tools/GetWebBrowser",
            tools__pb2.WebBrowserRequest.SerializeToString,
            tools__pb2.WebBrowserResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def GetFileConverter(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/Tools/GetFileConverter",
            tools__pb2.FileConverterRequest.SerializeToString,
            tools__pb2.FileConverterResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def GetCodeRunner(
        request_iterator,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            "/Tools/GetCodeRunner",
            tools__pb2.CodeRunnerRequest.SerializeToString,
            tools__pb2.CodeRunnerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )
