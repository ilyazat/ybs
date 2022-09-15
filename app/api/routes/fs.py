from datetime import datetime, timedelta

from app.db.db import database, items_table, items_history
from app.models import SystemItemImportRequest, SystemItem
from fastapi import APIRouter, status
from sqlalchemy import text, update
import logging

router = APIRouter()

__been_changed = False
main = []


@router.on_event("startup")
async def startup():
    await database.connect()


@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@router.post("/imports")
async def load_records(imports: SystemItemImportRequest):
    for item in imports.items:
        query = items_table.insert().values(id=item.id,
                                            url=item.url,
                                            date=imports.updateDate,
                                            parent_id=item.parentId,
                                            item_type=item.type,
                                            size=item.size)
        await database.execute(query)
        query_history = items_history.insert().values(id=item.id,
                                                      url=item.url,
                                                      date=imports.updateDate,
                                                      parent_id=item.parentId,
                                                      item_type=item.type,
                                                      size=item.size)
        await database.execute(query_history)
    await sort_items()


async def sort_items():
    global main
    all_items = await get_all()  # plain
    parent_child = dict()
    plain = dict()
    roots = []
    res = None
    for item in all_items:
        if item.item_type == "FILE":
            item_ = SystemItem(id=item.id,
                               url=item.url,
                               parentId=item.parent_id,
                               type=item.item_type,
                               date=item.date,
                               size=item.size,
                               children=None
                               )
        else:  # if a folder
            item_ = SystemItem(id=item.id,
                               url=item.url,
                               parentId=item.parent_id,
                               type=item.item_type,
                               date=item.date,
                               size=item.size,
                               children=[]
                               )
            if item.id not in parent_child:
                parent_child[item.id] = []

        plain.update({item_.id: item_})
        if item_.parentId and item_.parentId != "None":
            if item_.parentId not in parent_child:
                parent_child[item_.parentId] = []
            lst = parent_child[item_.parentId]
            lst.append(item_)

        else:  # if item has no parent => it is located in the root directory
            roots.append(item_.id)
    for root in roots:
        for folder in parent_child[root]:
            if folder.id in plain:
                folder.children = parent_child[folder.id]
    for root in roots:
        res = SystemItem(id=plain[root].id,
                         url=plain[root].url,
                         parentId=plain[root].parentId,
                         type=plain[root].type,
                         size=plain[root].size,
                         date=plain[root].date,
                         children=parent_child[root]
                         )
        res = _reset_size_of_folders(res)
        res = _sum(res)
        await _system_item_into_database(res)
    return res


def _reset_size_of_folders(folder):
    if folder.type == "FOLDER":
        folder.size = 0
    for item in folder.children:
        if item.children is not None:
            _reset_size_of_folders(item)
            folder.size = 0
    return folder


def _sum(folder: SystemItem) -> SystemItem:
    sum_folder = folder.size
    for item in folder.children:
        if item.children is not None:
            _sum(item)
            sum_folder += item.size
        else:
            sum_folder += item.size
    folder.size = sum_folder
    return folder


async def _system_item_into_database(folder: SystemItem) -> None:
    query = text(
        f"UPDATE items SET id='{folder.id}', date='{folder.date}', parent_id='{folder.parentId}', item_type='{folder.type}', " \
        f"size='{folder.size}' where id='{folder.id}'")
    await database.execute(query)

    for item in folder.children:
        if item.children is not None:
            await _system_item_into_database(item)
        print()
        print(item)
        # for items inside folder except other folders
        query = text(
            f"UPDATE items SET id='{item.id}', date='{item.date}', parent_id='{item.parentId}', item_type='{item.type}', " \
            f"size='{item.size}' where id='{item.id}'")
        await database.execute(query)


async def get_all():
    return await database.fetch_all(items_table.select())


@router.get("/nodes/{id}")
async def get_item(item_id: str):
    await sort_items()
    query = items_table.select().where(items_table.c.id == item_id)
    res = await database.fetch_one(query)
    return res


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def remove_item(item_id: str):
    item = await get_item(item_id)
    if item.item_type == "FOLDER":
        for id_ in await database.fetch_all(items_table.select().where(items_table.c.parent_id == item_id)):
            if id_.id:
                await remove_item(id_.id)

    query = items_table.delete().where(items_table.c.id == item_id)
    await database.execute(query)

# @router.get("/updates")
# async def get_updates(date_str: str):
#     date_datetime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
#     query = items_table.select().where(datetime.fromisoformat(items_table.c.date) > (date_datetime - timedelta(days=1)))
#
#     res = await database.fetch_all(query)
#
#     print(res)
#     return res
#