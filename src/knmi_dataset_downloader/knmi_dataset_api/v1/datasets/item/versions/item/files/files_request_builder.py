from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from .......models.list_files_response import ListFilesResponse
    from .get_order_by_query_parameter_type import GetOrderByQueryParameterType
    from .get_sorting_query_parameter_type import GetSortingQueryParameterType
    from .item.with_filename_item_request_builder import WithFilenameItemRequestBuilder

class FilesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /v1/datasets/{datasetName}/versions/{versionId}/files
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, Dict[str, Any]]) -> None:
        """
        Instantiates a new FilesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/v1/datasets/{datasetName}/versions/{versionId}/files{?begin*,end*,maxKeys*,nextPageToken*,orderBy*,sorting*,startAfterFilename*}", path_parameters)
    
    def by_filename(self,filename: str) -> WithFilenameItemRequestBuilder:
        """
        Gets an item from the knmi_dataset_api.v1.datasets.item.versions.item.files.item collection
        param filename: Name of the file
        Returns: WithFilenameItemRequestBuilder
        """
        if filename is None:
            raise TypeError("filename cannot be null.")
        from .item.with_filename_item_request_builder import WithFilenameItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["filename"] = filename
        return WithFilenameItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[FilesRequestBuilderGetQueryParameters]] = None) -> Optional[ListFilesResponse]:
        """
        Get paginated list of files for dataset
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ListFilesResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .......models.list_files_response import ListFilesResponse

        return await self.request_adapter.send_async(request_info, ListFilesResponse, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[FilesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get paginated list of files for dataset
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> FilesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: FilesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return FilesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class FilesRequestBuilderGetQueryParameters():
        """
        Get paginated list of files for dataset
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "max_keys":
                return "maxKeys"
            if original_name == "next_page_token":
                return "nextPageToken"
            if original_name == "order_by":
                return "orderBy"
            if original_name == "start_after_filename":
                return "startAfterFilename"
            if original_name == "begin":
                return "begin"
            if original_name == "end":
                return "end"
            if original_name == "sorting":
                return "sorting"
            return original_name
        
        # This parameter controls filtering (together with end). It defines the lower limit of the requested data. If ordering by filename, provide a string. If ordering by lastModified or created, provide a timestamp.
        begin: Optional[str] = None

        # This parameter controls filtering (together with begin). It defines the upper limit of the requested data. If ordering by filename, provide a string. If ordering by lastModified or created, provide a timestamp.
        end: Optional[str] = None

        # Maximum number of files to return
        max_keys: Optional[int] = None

        # Token to retrieve the next page of results. This token is returned by the API if the result set is larger than the maximum number of files to return.
        next_page_token: Optional[str] = None

        # Order the files by filename, timestamp of creation or timestamp of last modification
        order_by: Optional[GetOrderByQueryParameterType] = None

        # Sort the files in ascending or descending order
        sorting: Optional[GetSortingQueryParameterType] = None

        # Provide a filename to start listing after. Note: This deprecated parameter cannot be combined with orderBy, begin, end or sorting. Instead, use `nextPageToken`.
        start_after_filename: Optional[str] = None

    
    @dataclass
    class FilesRequestBuilderGetRequestConfiguration(RequestConfiguration[FilesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

