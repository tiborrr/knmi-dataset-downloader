from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

@dataclass
class FileSummary(Parsable):
    # The created property
    created: Optional[str] = None
    # The filename property
    filename: Optional[str] = None
    # The lastModified property
    last_modified: Optional[str] = None
    # The size property
    size: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FileSummary:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FileSummary
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return FileSummary()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        fields: Dict[str, Callable[[Any], None]] = {
            "created": lambda n : setattr(self, 'created', n.get_str_value()),
            "filename": lambda n : setattr(self, 'filename', n.get_str_value()),
            "lastModified": lambda n : setattr(self, 'last_modified', n.get_str_value()),
            "size": lambda n : setattr(self, 'size', n.get_int_value()),
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
        writer.write_str_value("created", self.created)
        writer.write_str_value("filename", self.filename)
        writer.write_str_value("lastModified", self.last_modified)
        writer.write_int_value("size", self.size)
    

