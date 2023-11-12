import traceback
from typing import List
from webbrowser import get
from fastapi import FastAPI, Depends, HTTPException, Query, status, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from enum import Enum
import pandas as pd
import numpy as np

from main import model, schema
from .database import SessionLocal, engine
model.Base.metadata.create_all(bind=engine)

app  = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Phương thức GET
# 1. Tìm kiếm sản phẩm theo tên : ERRORRRRRRRRRRRRRRRR
@app.get("/products/search", description = 'Search product details by name')
def search_product(product_name: str = Query(default=None, max_length=40), db: Session = Depends(get_db)):

    result = db.query(model.Product).filter(model.Product.ProductName.ilike(f"%{product_name}%")).all()
    names = np.array([row.ProductName for row in result])
    return {"Quantity":names.size,"Name of products":names.tolist(), "Product details": result}

# 2. Danh sách khách hàng đã mua sản phẩm theo ProductID : ERRORRRRRRRRRRRRRRRR
@app.get("/products/customers/{product_id}", response_model=List[schema.Customer])
def get_product_customers(product_id: int, db: Session = Depends(get_db)):
    # Sử dụng truy vấn SQL để lấy danh sách các khách hàng đã mua sản phẩm dựa trên mã sản phẩm
    query = f"""
    SELECT C.*
    FROM customers C
    INNER JOIN orders O ON C.CustomerID = O.CustomerID
    INNER JOIN orderdetails OD ON O.OrderID = OD.OrderID
    WHERE OD.ProductID = {product_id}
    """
    
    # Thực hiện truy vấn SQL và lấy kết quả
    result = pd.read_sql_query(query, db.connection())
    print("Hello")
    # Chuyển kết quả thành danh sách các bản ghi (records)
    records = result.to_dict(orient='records')
    
    return records

# 3. Lấy sản phẩm trong kho
# Tổng sản phẩm trong kho
def calculate_total_stock(product_data):
    total_stock = int(np.sum([product.get('UnitsInStock', 0) for product in product_data]))
    return total_stock
@app.get("/product/stock")
def get_product_stock(db: Session = Depends(get_db)):
    query = """
        SELECT ProductID, ProductName, UnitsInStock FROM products;
    """
    try:
        df = pd.read_sql_query(query, db.bind)
        # Sản phẩm tồn kho
        product_data = df.to_dict('records')
        # Tổng số sản phẩm còn lại
        total_stock = calculate_total_stock(product_data)

        return {"Total_stock": total_stock, "Product": product_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4. Danh sách hóa đơn theo EmployeeID
@app.get("/employee/invoices", response_model=List[schema.OrderDetails])
def get_employee_invoices(employee_id: int, db: Session = Depends(get_db)):
    # Sử dụng truy vấn SQL để lấy danh sách các hoá đơn của nhân viên
    query = f"""
    SELECT OD.*
    FROM orderdetails OD
    INNER JOIN orders O ON OD.OrderID = O.OrderID
    WHERE O.EmployeeID = {employee_id}
    """
    
    # Thực hiện truy vấn SQL và lấy kết quả
    result = pd.read_sql_query(query, db.connection())
    
    # Chuyển kết quả thành danh sách các bản ghi (records)
    records = result.to_dict(orient='records')
    
    return records

# 5. Đếm số lượng hóa đơn của 1 nhân viên
@app.get("/employee/totalInvoice")
def get_employee_invoice_count(employee_id: int, db: Session = Depends(get_db)):
    # Sử dụng truy vấn SQL để đếm số lượng hoá đơn của nhân viên dựa trên mã nhân viên
    query = f"""
    SELECT EmployeeID, OrderID
    FROM orders
    WHERE EmployeeID = {employee_id}
    """
    
    # Thực hiện truy vấn SQL và lấy kết quả
    result = pd.read_sql_query(query, db.connection())
    
    # Lấy số lượng hoá đơn từ kết quả truy vấn
    invoice_count = np.array([result["OrderID"]]).size
    
    # Trả về kết quả dưới dạng JSON
    return {"employee_id": employee_id, "total_invoice": invoice_count}

# 6. In chi tiết hóa đơn theo OrderID
@app.get("/orderdetail", description='Get invoice information by OrderID')
def info_invoice( db: Session = Depends(get_db), orderID: int = Query()):
 
    orderIDs = np.array(db.query(model.Orders.OrderID).all())
    if orderID not in orderIDs:
        raise HTTPException(status_code= 400, detail= f'OrderID not found. OrderID greater than {orderIDs[0]} and less than {orderIDs[-1]}')
    
    query = db.query(model.Product.ProductName,
                     model.OrderDetails.Quantity, 
                     model.OrderDetails.UnitPrice, 
                     model.OrderDetails.Discount, 
                     model.Orders.CustomerID, 
                     model.Orders.OrderDate).\
            join(model.OrderDetails, model.Product.ProductID == model.OrderDetails.ProductID).\
            join(model.Orders, model.Orders.OrderID == model.OrderDetails.OrderID).\
            filter(model.Orders.OrderID == orderID).all()
    df = pd.DataFrame(query, columns=['ProductName', 'Quantity', 'UnitPrice','Discount','CustomerID', 'OrderDate'])
    
    total_order_value = (df['Quantity'] * df['UnitPrice'] * (1-df['Discount'])).sum()
    
    return {
        "OrderDate": str(df['OrderDate'].iloc[0])[0:10],
        "CustomerID": df['CustomerID'].iloc[0],
        "Quantity": df.shape[0],
        "Products": df.drop(["OrderDate","CustomerID"], axis = 'columns').to_dict(orient='records'),
        "TotalOrderValue": total_order_value,
    }

# 7. Lấy danh sách khách hàng
@app.get("/customers/", response_model=List[schema.Customer])
def read_od11(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    items = db.query(model.Customer).offset(skip).limit(limit).all()
    df = pd.DataFrame([item.__dict__ for item in items])
    df["Fax"] = df["Fax"].fillna("N/A")
    df["PostalCode"] = df["PostalCode"].fillna("N/A")
    return df.to_dict(orient="records")

# 8. Lấy doanh thu theo thời gian
def get_daily_revenue(db: Session = Depends(get_db)):
    query = """
        SELECT O.OrderDate, SUM(OD.UnitPrice * OD.Quantity * (1 - OD.Discount)) AS DailyRevenue
        FROM orders AS O
        JOIN orderdetails AS OD ON O.OrderID = OD.OrderID
        GROUP BY O.OrderDate
        ORDER BY O.OrderDate;
    """
    try:
        result = pd.read_sql_query(query, db.bind)
        # Định dạng chuẩn cho OrderDate
        result['OrderDate'] = pd.to_datetime(result['OrderDate']).dt.date
        return result.to_dict(orient='records')
    except Exception as e:
        print(f"Đã xuất hiện lỗi: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_monthly_revenue(db: Session = Depends(get_db)):
    query = """
        SELECT 
            EXTRACT(MONTH FROM O.OrderDate) AS Month,
            EXTRACT(YEAR FROM O.OrderDate) AS Year,
            SUM(OD.UnitPrice * OD.Quantity * (1 - OD.Discount)) AS MonthlyRevenue
        FROM orders AS O
        JOIN orderdetails AS OD ON O.OrderID = OD.OrderID
        GROUP BY Year, Month
        ORDER BY Year, Month;
    """
    try:
        result = pd.read_sql_query(query, db.bind)
        # Chuyển đổi Month và Year thành kiểu int để tránh lỗi khi sử dụng chúng trong JSON
        result['Month'] = result['Month'].astype(int)
        result['Year'] = result['Year'].astype(int)
        return result.to_dict(orient='records')
    except Exception as e:
        print(f"Đã xuất hiện lỗi: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
def get_yearly_revenue(db: Session = Depends(get_db)):
    query = """
        SELECT 
            EXTRACT(YEAR FROM O.OrderDate) AS Year,
            SUM(OD.UnitPrice * OD.Quantity * (1 - OD.Discount)) AS YearlyRevenue
        FROM orders AS O
        JOIN orderdetails AS OD ON O.OrderID = OD.OrderID
        GROUP BY Year
        ORDER BY Year;
    """
    try:
        result = pd.read_sql_query(query, db.bind)
        # Chuyển đổi Year thành kiểu int để tránh lỗi khi sử dụng chúng trong JSON
        result['Year'] = result['Year'].astype(int)
        
        return result.to_dict(orient='records')
    except Exception as e:
        print(f"Đã xuất hiện lỗi: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/revenue/{time_period}")
def get_revenue_by_period(time_period: str, db: Session = Depends(get_db)):
    if time_period == "daily":
        return get_daily_revenue(db)
    elif time_period == "monthly":
        return get_monthly_revenue(db)
    elif time_period == "yearly":
        return get_yearly_revenue(db)
    else:
        raise HTTPException(status_code=400, detail="Invalid time period. Allowed values: daily, monthly, yearly")


# Phương thức POST
# 1. Thêm danh mục sản phẩm
@app.post("/category", description='Add categories')
def create_category(cate: schema.CategoryCreate, db: Session = Depends(get_db)):
    if not cate.CategoryName or not cate.Description:
        raise HTTPException(status_code=400, detail="All fields must be provided")
    
    db_cate = db.query(model.Category).filter(model.Category.CategoryName == cate.CategoryName).first()
    if db_cate:
        raise HTTPException(status_code=400, detail="CategoryName already exists")
    
    db_cate = model.Category(CategoryName = cate.CategoryName, Description = cate.Description)
    if len(db_cate.CategoryName) > 15:
        db_cate.CategoryName = np.where(len(db_cate.CategoryName) > 15, db_cate.CategoryName[:15], db_cate.CategoryName)

    try:
        db.add(db_cate)
        db.commit()
        # Làm mới đối tượng để lấy thông tin đã được lưu vào cơ sở dữ liệu
        db.refresh(db_cate)
        return db_cate
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create category: {str(e)}")


# 2. Thêm shipper
@app.post("/shipper/upload-data", description = 'Add shipper from file_csv')
async def upload_csv_shippers_file(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File is not a CSV")
    
    df = pd.read_csv(file.file)

    shippers = []
    # iterrows chạy theo chỉ số dòng và dữ liệu dòng
    for index, row in df.iterrows():
        csv_CompanyName = row['CompanyName']
        csv_Phone = row['Phone']
        exist_Shipper = db.query(model.Shipper).filter(model.Shipper.CompanyName == csv_CompanyName, model.Shipper.Phone == csv_Phone).first()
        if exist_Shipper is None:
            shipper = model.Shipper(CompanyName=csv_CompanyName, Phone=csv_Phone)
            shippers.append(shipper)

    if shippers == []:
        raise HTTPException(status_code=400, detail="Data already exists or the file does not have matching data")

    db.add_all(shippers)
    db.commit()
    return "CSV file uploaded and shippers added successfully"


# 3. Thêm sản phẩm
@app.post("/products/upload-data", description = "Upload CSV file to import customers")
async def upload_csv_products_file(file: UploadFile, db: Session = Depends(get_db)):
    # Kiểm tra định dạng file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File is not a CSV")
    try:
        df = pd.read_csv(file.file)

        products = []
        for idx, row in df.iterrows():
            csv_ProductName = row['ProductName']
            csv_SupplierID = row['SupplierID']
            csv_CategoryID = row['CategoryID']
            csv_QuantityPerUnit = row['QuantityPerUnit']
            csv_UnitPrice = row['UnitPrice']
            csv_UnitsInStock = row['UnitsInStock']
            csv_UnitsOnOrder = row['UnitsOnOrder']
            csv_ReorderLevel = row['ReorderLevel']
            csv_Discontinued = row['Discontinued']
            exist_Product = db.query(model.Product).filter(model.Product.ProductName == csv_ProductName).first()
                                                        #    model.Product.SupplierID == csv_SupplierID,
                                                        #    model.Product.CategoryID == csv_CategoryID,
                                                        #    model.Product.QuantityPerUnit == csv_QuantityPerUnit,
                                                        #    model.Product.UnitPrice == csv_UnitPrice,
                                                        #    model.Product.UnitsInStock == csv_UnitsInStock,
                                                        #    model.Product.UnitsOnOrder == csv_UnitsOnOrder,
                                                        #    model.Product.ReorderLevel == csv_ReorderLevel,
                                                        #    model.Product.Discontinued == csv_Discontinued).
            if exist_Product is None:
                product = model.Product(ProductName = csv_ProductName,
                                        SupplierID = csv_SupplierID,
                                        CategoryID = csv_CategoryID,
                                        QuantityPerUnit = csv_QuantityPerUnit,
                                        UnitPrice = csv_UnitPrice,
                                        UnitsInStock = csv_UnitsInStock,
                                        UnitsOnOrder = csv_UnitsOnOrder,
                                        ReorderLevel = csv_ReorderLevel,
                                        Discontinued = csv_Discontinued)
                products.append(product)
        
        if products == [] : # Nếu không có sản phẩm được khởi tạo trả về lỗi người dùng : 400
            raise HTTPException(status_code=400, detail="Data already exists or the file does not have matching data")
        
        db.add_all(products)
        db.commit()

        return "CSV file uploaded success"
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 4. Thêm khách hàng
@app.post("/customers/upload-data", description="Upload CSV file to import customers")
async def upload_csv_to_customers(file: UploadFile , db: Session = Depends(get_db)):
    # Kiểm tra định dạng file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File is not a CSV")

    try:
        df = pd.read_csv(file.file)
        # Kiểm tra các cột xem tồn tại không
        required_columns = {'CustomerID', 'CompanyName', 'ContactName', 'ContactTitle', 'Address', 'City', 'PostalCode', 'Country', 'Phone', 'Fax'}
        if not required_columns.issubset(df.columns): 
            missing_cols = required_columns - set(df.columns)
            raise HTTPException(status_code=422, detail=f"Missing columns: {missing_cols}")

        customer_dicts = df.to_dict(orient='records')
        
        # Sử dụng unpacking(**) để tạo danh sách  
        customers = [model.Customer(**data) for data in customer_dicts]
        
        db.add_all(customers)
        db.commit()

        return {"message": "Added customers successfully!", "count": len(customers)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 5. Thêm nhà cung cấp
@app.post("/supplier")
def create_supplier(sup: schema.SupplierCreate, db: Session = Depends(get_db)):
    existing_supplier = db.query(model.Supplier).filter(
        model.Supplier.CompanyName == sup.CompanyName,
        model.Supplier.ContactName == sup.ContactName,
        model.Supplier.ContactTitle == sup.ContactTitle,
        model.Supplier.PostalCode == sup.PostalCode
    ).first()
    
    if existing_supplier:
        raise HTTPException(status_code=400, detail="This supplier already exists in the database.")
    
    df = pd.DataFrame.from_dict(sup.dict(), orient='index').T
    if (df['PostalCode'].str.len() > 10).any():
        raise HTTPException(status_code=400, detail="PostalCode length limited to 10 characters.")
    
    try:
        db_sup = df.to_dict(orient='records')[0]
        db.add(model.Supplier(**db_sup))
        db.commit()
        return {"Message":'Add supplier is successful', "Detail": db_sup}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create supplier: {str(e)}")
    

# 6. Thêm hóa đơn
@app.post("/orders/")
def create_order(order: schema.OrderCreate, db: Session = Depends(get_db)):
    # Validate order data using NumPy
    valid_order = np.all(order.OrderDate is not None)

    if not valid_order:
        raise HTTPException(status_code=400, detail="Invalid order data")

    # Create a new order and add it to the database
    db_order = model.Orders(**order.dict(exclude={"Products"}))
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Create OrderDetails records for each product in the order
    for product_data in order.Products:
        valid_product_data = np.all(product_data.UnitPrice > 0) and np.all(product_data.Quantity > 0)
        if not valid_product_data:
            raise HTTPException(status_code=400, detail="Invalid product data")

        db_order_detail = model.OrderDetails(
            OrderID=db_order.OrderID,
            ProductID=product_data.ProductID,
            Quantity=product_data.Quantity,
            UnitPrice=product_data.UnitPrice,
            Discount=product_data.Discount
        )
        db.add(db_order_detail)

    db.commit()
    db.refresh(db_order)

    return db_order      