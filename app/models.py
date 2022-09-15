from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

SystemItemType = str  # тип элемента - папка или файл


class SystemItem(BaseModel):
    """
    Arguments:
        item_id -- Уникальный идентификатор
        url -- Ссылка на файл. Для папок поле равнно null.
        date -- Время последнего обновления элемента.
        parent_id -- id родительской папки


    """
    id: str
    url: str = None
    parentId: str = None
    type: SystemItemType
    size: int = 0
    date: str
    children: list[SystemItem] = None


class SystemItemImport(BaseModel):
    id: str
    url: str = None
    parentId: str = None
    type: SystemItemType
    size: int = 0


class SystemItemImportRequest(BaseModel):
    """
    Args:
        items - импортируемые элементы
        updateDate - строка-datetime - время обновления добавляемых элементов
    """
    items: list[SystemItemImport]
    updateDate: str


class SystemItemHistoryUnit(BaseModel):
    id: str
    url: str = None
    parent_id: str = None
    item_type: SystemItemType
    size: int = 0
    date: str


class SystemItemHistoryResponse(BaseModel):
    items: list[SystemItemHistoryUnit]


class Error(BaseModel):
    code: int
    message: str
