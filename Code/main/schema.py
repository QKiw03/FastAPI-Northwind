# from fastapi import BaseModel 
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
from typing import Union, List

class Product(BaseModel):
    ProductID : int
    ProductName : str
    SupplierID : int
    CategoryID : int
    QuantityPerUnit : str
    UnitPrice : float
    UnitsInStock : int
    UnitsOnOrder : int
    ReorderLevel : int
    Discontinued : int

    class Config:
        from_attributes = True

class OrderDetails(BaseModel):
    OrderID : int
    ProductID : int
    UnitPrice : float
    Quantity : int
    Discount : float

    class Config:
        from_attributes = True

# post order
class OrderProductCreate(BaseModel):
    ProductID: int
    Quantity: int
    UnitPrice: float
    Discount: float

class OrderCreate(BaseModel):
    CustomerID: str
    EmployeeID: int
    OrderDate: datetime
    Products: List[OrderProductCreate]

class Customer(BaseModel):
    CustomerID : str
    CompanyName : str
    ContactName : str
    ContactTitle : str
    Address : str
    City : str
    PostalCode : str
    Country : str
    Phone : str
    Fax : str

    class Config:
        from_attributes = True

class Shipper(BaseModel):
    ShipperID: int
    CompanyName: str
    Phone: str
    class Config:
        from_attributes = True

class SupplierBase(BaseModel):
    CompanyName :str
    ContactName :str
    ContactTitle :str
    Address :str
    City :str
    Region :str
    PostalCode :str
    Country :str
    Phone :str
    Fax :str
    HomePage :str

class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    SupplierID: int
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    CategoryName: str
    Description: str 

class CategoryCreate(CategoryBase):
# đầu vào khi post chỉ có thuộc tính trong CategoryBase
    pass
# có id thì có thể nhập id hoặc không(AI)
    # id: int

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class DailyRevenue(BaseModel):
    OrderDate: date
    DailyRevenue: float
    # class Config:
    #     from_attributes = True

class MonthlyRevenue(BaseModel):
    Month: int
    Year: int
    MonthlyRevenue: float
    # class Config:
    #     from_attributes = True

class YearlyRevenue(BaseModel):
    Year: int
    YearlyRevenue: float
    # class Config:
    #     from_attributes = True





    