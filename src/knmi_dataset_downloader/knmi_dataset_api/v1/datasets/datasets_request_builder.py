from __future__ import annotations
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_dataset_name_item_request_builder import WithDatasetNameItemRequestBuilder

class DatasetsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /v1/datasets
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, Dict[str, Any]]) -> None:
        """
        Instantiates a new DatasetsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/v1/datasets", path_parameters)
    
    def by_dataset_name(self,dataset_name: str) -> WithDatasetNameItemRequestBuilder:
        """
        Gets an item from the knmi_dataset_api.v1.datasets.item collection
        param dataset_name: Name of the dataset
        Returns: WithDatasetNameItemRequestBuilder
        """
        if dataset_name is None:
            raise TypeError("dataset_name cannot be null.")
        from .item.with_dataset_name_item_request_builder import WithDatasetNameItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["datasetName"] = dataset_name
        return WithDatasetNameItemRequestBuilder(self.request_adapter, url_tpl_params)
    

