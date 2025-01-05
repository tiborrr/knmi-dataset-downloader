from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .file_summary import FileSummary

@dataclass
class ListFilesResponse(Parsable):
    # The files property
    files: Optional[List[FileSummary]] = None
    # The isTruncated property
    is_truncated: Optional[bool] = None
    # The maxResults property
    max_results: Optional[int] = None
    # The nextPageToken property
    next_page_token: Optional[str] = None
    # The resultCount property
    result_count: Optional[int] = None
    # The startAfterFilename property
    start_after_filename: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ListFilesResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ListFilesResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ListFilesResponse()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .file_summary import FileSummary

        from .file_summary import FileSummary

        fields: Dict[str, Callable[[Any], None]] = {
            "files": lambda n : setattr(self, 'files', n.get_collection_of_object_values(FileSummary)),
            "isTruncated": lambda n : setattr(self, 'is_truncated', n.get_bool_value()),
            "maxResults": lambda n : setattr(self, 'max_results', n.get_int_value()),
            "nextPageToken": lambda n : setattr(self, 'next_page_token', n.get_str_value()),
            "resultCount": lambda n : setattr(self, 'result_count', n.get_int_value()),
            "startAfterFilename": lambda n : setattr(self, 'start_after_filename', n.get_str_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        from .file_summary import FileSummary

        writer.write_collection_of_object_values("files", self.files)
        writer.write_bool_value("isTruncated", self.is_truncated)
        writer.write_int_value("maxResults", self.max_results)
        writer.write_str_value("nextPageToken", self.next_page_token)
        writer.write_int_value("resultCount", self.result_count)
        writer.write_str_value("startAfterFilename", self.start_after_filename)
    

