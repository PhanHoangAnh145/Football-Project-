import requests
import argparse
import csv
from tabulate import tabulate


def lookup():
    # 1. Thiết lập nhận tham số từ dòng lệnh (Terminal)
    parser = argparse.ArgumentParser(description="Tra cứu chỉ số cầu thủ")
    parser.add_argument('--name', type=str, help="Tên cầu thủ cần tìm")
    parser.add_argument('--club', type=str, help="Tên câu lạc bộ cần tìm")
    args = parser.parse_args()

    url = ""
    filename = ""

    # 2. Xác định URL API dựa trên tham số đầu vào
    if args.name:
        url = f"http://127.0.0.1:5000/api/player?name={args.name}"
        filename = f"{args.name}.csv"
    elif args.club:
        # Lưu ý: Bạn cần đảm bảo API /api/club ở câu II.1 đã hoạt động đúng
        url = f"http://127.0.0.1:5000/api/club?name={args.club}"
        filename = f"{args.club}.csv"
    else:
        print("Vui lòng nhập --name hoặc --club")
        return

    # 3. Gửi request đến Flask Server
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            # Nếu trả về 1 cầu thủ (dict), cho vào list để vẽ bảng
            if isinstance(data, dict):
                data = [data]

            # 4. In kết quả ra màn hình dạng bảng
            print(f"\nKết quả tra cứu cho: {args.name or args.club}")
            print(tabulate(data, headers="keys", tablefmt="grid"))

            # 5. Xuất ra file CSV
            if data:
                keys = data[0].keys()
                with open(filename, 'w', newline='', encoding='utf-8-sig') as output_file:
                    dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(data)
                print(f"\n[Thành công] Đã lưu dữ liệu vào file: {filename}")
        else:
            print(f"Lỗi: {response.json().get('message', 'Không tìm thấy dữ liệu')}")

    except requests.exceptions.ConnectionError:
        print("Lỗi: Không thể kết nối đến Server Flask. Hãy đảm bảo app.py đang chạy!")


if __name__ == "__main__":
    lookup()