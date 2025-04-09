from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

import dynamic_tables
import schemas
from database import get_db
from auth import get_current_user

# Create router for dynamic tables
dynamic_tables_router = APIRouter(prefix="/tables", tags=["Dynamic Tables"])

# Table Definition Endpoints
@dynamic_tables_router.post("/", response_model=schemas.TableDefinition)
async def create_table(
    table: schemas.TableDefinitionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new table definition with columns.
    
    This endpoint allows you to define a new table structure with custom columns.
    Each column can have different data types and constraints.
    """
    return dynamic_tables.create_table_definition(db, table, current_user.user_id)

@dynamic_tables_router.get("/", response_model=List[schemas.TableDefinition])
async def get_tables(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all table definitions.
    
    Returns a list of all table definitions with their columns.
    """
    return dynamic_tables.get_table_definitions(db, skip, limit)

@dynamic_tables_router.get("/{table_id}", response_model=schemas.TableDefinition)
async def get_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a specific table definition by ID.
    
    Returns the table definition with all its columns.
    """
    return dynamic_tables.get_table_definition(db, table_id)

@dynamic_tables_router.put("/{table_id}", response_model=schemas.TableDefinition)
async def update_table(
    table_id: int,
    table: schemas.TableDefinitionBase,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update a table definition.
    
    This endpoint allows you to update the name and description of a table.
    Note that you cannot update columns through this endpoint.
    """
    return dynamic_tables.update_table_definition(db, table_id, table)

@dynamic_tables_router.delete("/{table_id}")
async def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a table definition.
    
    This will delete the table definition and all its columns and data.
    """
    return dynamic_tables.delete_table_definition(db, table_id)

# Column Definition Endpoints
@dynamic_tables_router.post("/{table_id}/columns", response_model=schemas.ColumnDefinition)
async def create_column(
    table_id: int,
    column: schemas.ColumnDefinitionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Add a new column to a table.
    
    This endpoint allows you to add a new column to an existing table.
    """
    return dynamic_tables.create_column_definition(db, column, table_id)

@dynamic_tables_router.get("/{table_id}/columns", response_model=List[schemas.ColumnDefinition])
async def get_columns(
    table_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all columns for a table.
    
    Returns a list of all columns defined for the specified table.
    """
    return dynamic_tables.get_column_definitions_by_table(db, table_id)

@dynamic_tables_router.get("/{table_id}/columns/{column_id}", response_model=schemas.ColumnDefinition)
async def get_column(
    table_id: int,
    column_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a specific column by ID.
    
    Returns the column definition for the specified column.
    """
    column = dynamic_tables.get_column_definition(db, column_id)
    if column.table_id != table_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found in this table"
        )
    return column

@dynamic_tables_router.put("/{table_id}/columns/{column_id}", response_model=schemas.ColumnDefinition)
async def update_column(
    table_id: int,
    column_id: int,
    column: schemas.ColumnDefinitionBase,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update a column definition.
    
    This endpoint allows you to update the properties of a column.
    """
    db_column = dynamic_tables.get_column_definition(db, column_id)
    if not db_column or db_column.table_id != table_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found in this table"
        )
    return dynamic_tables.update_column_definition(db, column_id, column)

@dynamic_tables_router.delete("/{table_id}/columns/{column_id}")
async def delete_column(
    table_id: int,
    column_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a column.
    
    This will delete the column definition and remove the column data from all rows.
    """
    db_column = dynamic_tables.get_column_definition(db, column_id)
    if not db_column or db_column.table_id != table_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found in this table"
        )
    return dynamic_tables.delete_column_definition(db, column_id)

# Table Data Endpoints
@dynamic_tables_router.post("/{table_id}/data", response_model=schemas.DynamicTableData)
async def create_row(
    table_id: int,
    data: schemas.DynamicTableDataCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Add a new row of data to a table.
    
    This endpoint allows you to add a new row of data to the specified table.
    The data must conform to the table's column definitions.
    """
    return dynamic_tables.create_table_row(db, table_id, data.data, current_user.user_id)

@dynamic_tables_router.get("/{table_id}/data", response_model=List[schemas.DynamicTableData])
async def get_rows(
    table_id: int,
    filter: Optional[str] = Query(None, description="JSON string of filter criteria"),
    sort: Optional[str] = Query(None, description="Field to sort by"),
    sort_dir: Optional[str] = Query("asc", description="Sort direction (asc or desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get rows of data from a table.
    
    Returns a list of rows from the specified table.
    You can filter and sort the results using query parameters.
    """
    skip = (page - 1) * page_size
    filter_params = json.loads(filter) if filter else None
    return dynamic_tables.get_table_rows(
        db, table_id, skip, page_size, filter_params, sort, sort_dir
    )

@dynamic_tables_router.get("/{table_id}/data/{row_id}", response_model=schemas.DynamicTableData)
async def get_row(
    table_id: int,
    row_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a specific row of data by ID.
    
    Returns the row data for the specified row.
    """
    return dynamic_tables.get_table_row(db, table_id, row_id)

@dynamic_tables_router.put("/{table_id}/data/{row_id}", response_model=schemas.DynamicTableData)
async def update_row(
    table_id: int,
    row_id: int,
    data: schemas.DynamicTableDataCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update a row of data.
    
    This endpoint allows you to update the data in a specific row.
    The data must conform to the table's column definitions.
    """
    return dynamic_tables.update_table_row(db, table_id, row_id, data.data)

@dynamic_tables_router.delete("/{table_id}/data/{row_id}")
async def delete_row(
    table_id: int,
    row_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a row of data.
    
    This will delete the specified row from the table.
    """
    return dynamic_tables.delete_table_row(db, table_id, row_id)