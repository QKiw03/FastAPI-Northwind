from sqlalchemy import Boolean, Column,Date,\
    Float, ForeignKey, Integer, String, Numeric, Text
from sqlalchemy.orm import relationship
from .database import Base


class Product(Base):
    __tablename__ = 'products'

    ProductID = Column(Integer, primary_key=True, autoincrement=True)
    ProductName = Column(String(40))
    SupplierID = Column(Integer,ForeignKey('suppliers.SupplierID'))
    CategoryID = Column(Integer,ForeignKey('categories.CategoryID'))
    QuantityPerUnit = Column(String(20))
    UnitPrice = Column(Numeric(19, 4))
    UnitsInStock = Column(Integer)
    UnitsOnOrder = Column(Integer)
    ReorderLevel = Column(Integer)
    Discontinued = Column(Boolean)

    orderdetails = relationship('OrderDetails', back_populates='product')
    category = relationship("Category", back_populates="product")
    supplier = relationship("Supplier", back_populates="product")

class OrderDetails(Base):
    __tablename__ = "orderdetails"

    OrderID = Column(Integer, ForeignKey('orders.OrderID'),primary_key=True, index=True)
    ProductID = Column(Integer,ForeignKey('products.ProductID'), primary_key=True, index=True)
    UnitPrice = Column(Float)
    Quantity = Column(Integer)
    Discount = Column(Float)

    product = relationship('Product', back_populates='orderdetails')
    orders = relationship('Orders', back_populates='orderdetails')
    # OrderID = Column(Integer, ForeignKey("Orders.OrderID"))
    # orders = relationship("Orders", back_populates="owner")

class Orders(Base):
    __tablename__= "orders"

    OrderID = Column(Integer, primary_key=True, autoincrement=True)
    CustomerID = Column(String(5),ForeignKey('customers.CustomerID'))
    EmployeeID = Column(Integer)
    OrderDate = Column(Date)

    orderdetails = relationship('OrderDetails', back_populates='orders')
    customer = relationship("Customer", back_populates="orders")
    # OrderID = Column(Integer, ForeignKey("OrderDetails.OrderID"))
    

class Customer(Base):
    __tablename__ = 'customers'

    CustomerID = Column(String(5), primary_key=True)
    CompanyName = Column(String(40))
    ContactName = Column(String(30))
    ContactTitle = Column(String(30))
    Address = Column(String(60))
    City = Column(String(15))
    PostalCode = Column(String(10))
    Country = Column(String(15))
    Phone = Column(String(24))
    Fax = Column(String(24))

    orders = relationship("Orders", back_populates="customer")    

class Category(Base):
    __tablename__ = 'categories'

    CategoryID = Column(Integer, primary_key=True, autoincrement = True)
    CategoryName = Column(String(15))
    Description = Column(Text)
    # Picture = Column(LargeBinary)

    product = relationship("Product", back_populates="category")

class Supplier(Base):
    __tablename__ = 'suppliers'

    SupplierID = Column(Integer, primary_key=True, autoincrement=True)
    CompanyName = Column(String(40))
    ContactName = Column(String(30))
    ContactTitle = Column(String(30))
    Address = Column(String(60))
    City = Column(String(15))
    Region = Column(String(15))
    PostalCode = Column(String(10))
    Country = Column(String(15))
    Phone = Column(String(24))
    Fax = Column(String(24))
    HomePage = Column(Text)

    product = relationship("Product", back_populates="supplier")

class Shipper(Base):
    __tablename__ = "shippers"
    
    ShipperID= Column(Integer, primary_key=True, autoincrement=True)
    CompanyName= Column(String(40))
    Phone = Column(String(24))


