from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

@dataclass
class FileDownload(Parsable):
    # The contentType property
    content_type: Optional[str] = None
    # The lastModified property
    last_modified: Optional[str] = None
    # The size property
    size: Optional[str] = None
    # The temporaryDownloadUrl property
    temporary_download_url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FileDownload:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FileDownload
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return FileDownload()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        fields: Dict[str, Callable[[Any], None]] = {
            "contentType": lambda n : setattr(self, 'content_type', n.get_str_value()),
            "lastModified": lambda n : setattr(self, 'last_modified', n.get_str_value()),
            "size": lambda n : setattr(self, 'size', n.get_str_value()),
            "temporaryDownloadUrl": lambda n : setattr(self, 'temporary_download_url', n.get_str_value()),
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
        writer.write_str_value("contentType", self.content_type)
        writer.write_str_value("lastModified", self.last_modified)
        writer.write_str_value("size", self.size)
        writer.write_str_value("temporaryDownloadUrl", self.temporary_download_url)
    

