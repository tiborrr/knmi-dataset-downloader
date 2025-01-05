from enum import Enum

class GetOrderByQueryParameterType(str, Enum):
    Filename = "filename",
    LastModified = "lastModified",
    Created = "created",

