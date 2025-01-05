from __future__ import annotations
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_version_item_request_builder import WithVersionItemRequestBuilder

class VersionsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /v1/datasets/{datasetName}/versions
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, Dict[str, Any]]) -> None:
        """
        Instantiates a new VersionsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/v1/datasets/{datasetName}/versions", path_parameters)
    
    def by_version_id(self,version_id: str) -> WithVersionItemRequestBuilder:
        """
        Gets an item from the knmi_dataset_api.v1.datasets.item.versions.item collection
        param version_id: Version of the dataset
        Returns: WithVersionItemRequestBuilder
        """
        if version_id is None:
            raise TypeError("version_id cannot be null.")
        from .item.with_version_item_request_builder import WithVersionItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["versionId"] = version_id
        return WithVersionItemRequestBuilder(self.request_adapter, url_tpl_params)
    

