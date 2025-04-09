from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
import models
import schemas
from typing import List, Dict, Any, Optional, Union
import json
from datetime import datetime, date
from fastapi import HTTPException, status

# Dynamic Table CRUD operations
def get_table_definition(db: Session, table_id: int):
    return db.query(models.TableDefinition).filter(models.TableDefinition.id == table_id).first()

def get_table_definition_by_name(db: Session, name: str):
    return db.query(models.TableDefinition).filter(models.TableDefinition.name == name).first()

def get_table_definitions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TableDefinition).offset(skip).limit(limit).all()

def create_table_definition(db: Session, table: schemas.TableDefinitionCreate, user_id: Optional[int] = None):
    # Check if table with same name exists
    if get_table_definition_by_name(db, name=table.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table with name '{table.name}' already exists"
        )
    
    db_table = models.TableDefinition(
        name=table.name,
        description=table.description,
        created_by=user_id
    )
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    
    # Add columns
    for column in table.columns:
        db_column = models.ColumnDefinition(
            table_id=db_table.id,
            name=column.name,
            description=column.description,
            column_type=column.column_type.value,
            is_required=column.is_required,
            is_unique=column.is_unique,
            is_primary_key=column.is_primary_key,
            is_index=column.is_index,
            default_value=column.default_value,
            max_length=column.max_length
        )
        db.add(db_column)
    
    db.commit()
    db.refresh(db_table)
    return db_table

def update_table_definition(db: Session, table_id: int, table: schemas.TableDefinitionBase):
    db_table = get_table_definition(db, table_id)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    
    # Check if new name conflicts with existing table
    if table.name != db_table.name and get_table_definition_by_name(db, name=table.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table with name '{table.name}' already exists"
        )
    
    db_table.name = table.name
    db_table.description = table.description
    db_table.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_table)
    return db_table

def delete_table_definition(db: Session, table_id: int):
    db_table = get_table_definition(db, table_id)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    
    # This will cascade delete all columns and data
    db.delete(db_table)
    db.commit()
    return {"message": "Table deleted successfully"}

def get_column_definition(db: Session, column_id: int):
    return db.query(models.ColumnDefinition).filter(models.ColumnDefinition.id == column_id).first()

def get_column_definitions_by_table(db: Session, table_id: int):
    return db.query(models.ColumnDefinition).filter(models.ColumnDefinition.table_id == table_id).all()

def create_column_definition(db: Session, column: schemas.ColumnDefinitionCreate, table_id: int):
    # Check if table exists
    db_table = get_table_definition(db, table_id)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    
    # Check if column with same name exists in this table
    existing_columns = get_column_definitions_by_table(db, table_id)
    for existing_column in existing_columns:
        if existing_column.name == column.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column with name '{column.name}' already exists in this table"
            )
    
    db_column = models.ColumnDefinition(
        table_id=table_id,
        name=column.name,
        description=column.description,
        column_type=column.column_type.value,
        is_required=column.is_required,
        is_unique=column.is_unique,
        is_primary_key=column.is_primary_key,
        is_index=column.is_index,
        default_value=column.default_value,
        max_length=column.max_length
    )
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column

def update_column_definition(db: Session, column_id: int, column: schemas.ColumnDefinitionBase):
    db_column = get_column_definition(db, column_id)
    if not db_column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Check if new name conflicts with existing column in the same table
    if column.name != db_column.name:
        existing_columns = get_column_definitions_by_table(db, db_column.table_id)
        for existing_column in existing_columns:
            if existing_column.name == column.name and existing_column.id != column_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Column with name '{column.name}' already exists in this table"
                )
    
    db_column.name = column.name
    db_column.description = column.description
    db_column.column_type = column.column_type.value
    db_column.is_required = column.is_required
    db_column.is_unique = column.is_unique
    db_column.is_primary_key = column.is_primary_key
    db_column.is_index = column.is_index
    db_column.default_value = column.default_value
    db_column.max_length = column.max_length
    
    db.commit()
    db.refresh(db_column)
    return db_column

def delete_column_definition(db: Session, column_id: int):
    db_column = get_column_definition(db, column_id)
    if not db_column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    db.delete(db_column)
    db.commit()
    return {"message": "Column deleted successfully"}

def validate_data_against_schema(data: Dict[str, Any], columns: List[models.ColumnDefinition]) -> Dict[str, str]:
    """Validate data against column definitions and return errors if any"""
    errors = {}
    
    # Check for required fields
    for column in columns:
        if column.is_required and column.name not in data:
            errors[column.name] = f"Field '{column.name}' is required"
            continue
            
        if column.name not in data:
            continue
            
        value = data[column.name]
        
        # Type validation
        if column.column_type == "string" or column.column_type == "text":
            if not isinstance(value, str):
                errors[column.name] = f"Field '{column.name}' must be a string"
            elif column.max_length and len(value) > column.max_length:
                errors[column.name] = f"Field '{column.name}' exceeds maximum length of {column.max_length}"
                
        elif column.column_type == "integer":
            try:
                int(value)
            except (ValueError, TypeError):
                errors[column.name] = f"Field '{column.name}' must be an integer"
                
        elif column.column_type == "float":
            try:
                float(value)
            except (ValueError, TypeError):
                errors[column.name] = f"Field '{column.name}' must be a number"
                
        elif column.column_type == "boolean":
            if not isinstance(value, bool) and value not in (0, 1, "true", "false", "True", "False"):
                errors[column.name] = f"Field '{column.name}' must be a boolean"
                
        elif column.column_type == "date":
            try:
                if isinstance(value, str):
                    datetime.strptime(value, "%Y-%m-%d").date()
                elif not isinstance(value, date):
                    errors[column.name] = f"Field '{column.name}' must be a valid date (YYYY-MM-DD)"
            except ValueError:
                errors[column.name] = f"Field '{column.name}' must be a valid date (YYYY-MM-DD)"
                
        elif column.column_type == "datetime":
            try:
                if isinstance(value, str):
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                elif not isinstance(value, datetime):
                    errors[column.name] = f"Field '{column.name}' must be a valid datetime"
            except ValueError:
                errors[column.name] = f"Field '{column.name}' must be a valid datetime"
                
        elif column.column_type == "json":
            if isinstance(value, str):
                try:
                    json.loads(value)
                except json.JSONDecodeError:
                    errors[column.name] = f"Field '{column.name}' must be valid JSON"
            elif not isinstance(value, (dict, list)):
                errors[column.name] = f"Field '{column.name}' must be valid JSON"
    
    return errors

def create_table_row(db: Session, table_id: int, data: Dict[str, Any], user_id: Optional[int] = None):
    # Get table definition
    table = get_table_definition(db, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    
    # Get column definitions
    columns = get_column_definitions_by_table(db, table_id)
    
    # Validate data against schema
    errors = validate_data_against_schema(data, columns)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"validation_errors": errors}
        )
    
    # Check for unique constraints
    for column in columns:
        if column.is_unique and column.name in data:
            # Check if value already exists
            existing_rows = db.query(models.DynamicTableData).filter(
                models.DynamicTableData.table_id == table_id
            ).all()
            
            for row in existing_rows:
                if column.name in row.data and row.data[column.name] == data[column.name]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Value '{data[column.name]}' already exists for field '{column.name}'"
                    )
    
    # Create row
    db_row = models.DynamicTableData(
        table_id=table_id,
        data=data,
        created_by=user_id
    )
    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row

def get_table_row(db: Session, table_id: int, row_id: int):
    row = db.query(models.DynamicTableData).filter(
        models.DynamicTableData.table_id == table_id,
        models.DynamicTableData.id == row_id
    ).first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Row not found"
        )
    
    return row

def get_table_rows(db: Session, table_id: int, skip: int = 0, limit: int = 100, 
                  filter_params: Optional[Dict[str, Any]] = None, 
                  sort_field: Optional[str] = None,
                  sort_direction: str = "asc"):
    # Check if table exists
    table = get_table_definition(db, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    
    query = db.query(models.DynamicTableData).filter(models.DynamicTableData.table_id == table_id)
    
    # Apply filters if provided
    if filter_params:
        # This is a simplified approach - in a real app, you'd need more sophisticated JSON filtering
        for field, value in filter_params.items():
            # For JSON fields, we need to use the -> operator in SQL
            # This is MySQL specific syntax
            query = query.filter(text(f"JSON_EXTRACT(data, '$.{field}') = '{value}'"))
    
    # Apply sorting if provided
    if sort_field:
        # Again, MySQL specific JSON sorting
        if sort_direction.lower() == "desc":
            query = query.order_by(text(f"JSON_EXTRACT(data, '$.{sort_field}') DESC"))
        else:
            query = query.order_by(text(f"JSON_EXTRACT(data, '$.{sort_field}') ASC"))
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

def update_table_row(db: Session, table_id: int, row_id: int, data: Dict[str, Any]):
    # Get row
    db_row = db.query(models.DynamicTableData).filter(
        models.DynamicTableData.table_id == table_id,
        models.DynamicTableData.id == row_id
    ).first()
    
    if not db_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Row not found"
        )
    
    # Get column definitions
    columns = get_column_definitions_by_table(db, table_id)
    
    # Validate data against schema
    errors = validate_data_against_schema(data, columns)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"validation_errors": errors}
        )
    
    # Check for unique constraints
    for column in columns:
        if column.is_unique and column.name in data:
            # Check if value already exists in other rows
            existing_rows = db.query(models.DynamicTableData).filter(
                models.DynamicTableData.table_id == table_id,
                models.DynamicTableData.id != row_id
            ).all()
            
            for row in existing_rows:
                if column.name in row.data and row.data[column.name] == data[column.name]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Value '{data[column.name]}' already exists for field '{column.name}'"
                    )
    
    # Update row
    # Merge existing data with new data
    updated_data = {**db_row.data, **data}
    db_row.data = updated_data
    db_row.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_row)
    return db_row

def delete_table_row(db: Session, table_id: int, row_id: int):
    db_row = db.query(models.DynamicTableData).filter(
        models.DynamicTableData.table_id == table_id,
        models.DynamicTableData.id == row_id
    ).first()
    
    if not db_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Row not found"
        )
    
    db.delete(db_row)
    db.commit()
    return {"message": "Row deleted successfully"}