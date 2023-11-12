
## Mô tả
- Ứng dụng numpy, pandas vào viết API
- Lấy và thêm dữ liệu vào database

## Cấu trúc
#### Gồm 2 thư mục chính :
+ Code : Nơi chứa môi trường và code thực thi
+ Data : Chứ database, file thuyết trình, file mô tả thông tin các endpoint, file thực thi khi thêm dữ liệu.

## Chuẩn bị
#### Database
- Tên : [Northwind](https://drive.google.com/uc?id=1gTwQZDrlmuWficfFLjnGN0R7zTLShG-s)
- Hệ quản trị sử dụng (DBMS): **MySQL**
- Yêu cầu : Đổi tên bảng '**order details**' =>  '**orderdetails**'
#### Môi trường 
- Ở đây chúng ta sử dụng môi trường ảo(biệt lập) của Python !
- Cài đặt thư viện **`virtualenv`** và gọi mô-đun **`venv`**
- Cài package *virtualenv* : **$ pip3 install virtualenv** 
- Cài đặt môi trường ảo : **$ python3 -m venv env**
- Lựa chọn version của python có **(env)**
- Cài đặt các package đi kèm: **$ pip install -r [necessary_lib.txt](https://drive.google.com/uc?export=download&id=1WwZO7iybEZXwF7muaciTYd0yOIECJbhE)**
## Thực thi code
- Đi tơi thư mục **Code** -> **Open terminal** -> **$ uvicorn main.main:app --reload**
- Tại đây ấn vào link: http://127.0.0.1:8000
- Tại brower ta thêm đuôi /docs : http://127.0.0.1:8000/docs để  sử dụng các endpoint do nhóm xây dựng

## Kết thúc
- Đây là dự án của nhóm **.py**
- Được sử dụng và tham khảo đóng góp ý kiến