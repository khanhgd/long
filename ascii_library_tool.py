#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASCII Library Management Tool (ASCLL)
Công cụ Quản lý Thư viện - Hệ thống quản lý mượn/trả sách tích hợp
developed by khanh 2007
"""

import os
import sys
import datetime
import uuid
import sqlite3

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.expanduser("~")

def running_on_termux() -> bool:
    """Detect running in Termux on Android."""
    return sys.platform.startswith("linux") and (
        "ANDROID_ROOT" in os.environ or
        "TERMUX_VERSION" in os.environ or
        "com.termux" in os.path.expanduser("~")
    )

APP_FOLDER = SCRIPT_DIR if os.access(SCRIPT_DIR, os.W_OK) and not running_on_termux() else os.path.join(HOME_DIR, ".ascii_library")
os.makedirs(APP_FOLDER, exist_ok=True)

DB_FILE_ACCESS = os.path.join(SCRIPT_DIR, "Database1.accdb")
DB_FILE_SQLITE = os.path.join(APP_FOLDER, "Database1.db")
USE_SQLITE = running_on_termux() or not (PYODBC_AVAILABLE and os.path.isfile(DB_FILE_ACCESS))
DB_FILE = DB_FILE_SQLITE if USE_SQLITE else DB_FILE_ACCESS
DRIVER = r"Microsoft Access Driver (*.mdb, *.accdb)"

# Table names
BORROWER_TABLE = "BẢNG HỌC SINH"
BOOK_TABLE = "BẢNG MÃ SÁCH"
BORROWING_RETURNING_TABLE = "BẢNG NGÀY MƯỢM NGÀY TRẢ"

# File storage folders - cross-platform writable folder
BORROW_FOLDER = os.path.join(APP_FOLDER, "borrow_records")
STUDENT_FOLDER = os.path.join(APP_FOLDER, "student_records")

# ============================================================================
# TOKEN AND CONNECTION UTILITIES
# ============================================================================

def generate_token():
    """Tạo token duy nhất"""
    return str(uuid.uuid4())[:8].upper()


def get_connection():
    """Kết nối đến cơ sở dữ liệu phù hợp với nền tảng."""
    if USE_SQLITE:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    conn_str = (
        fr"DRIVER={{{DRIVER}}};"
        fr"DBQ={DB_FILE};"
        r"Uid=Admin;Pwd=;"
    )
    return pyodbc.connect(conn_str)


def get_last_insert_id(cursor):
    """Lấy ID tự động tăng cuối cùng của bản ghi."""
    if USE_SQLITE:
        return cursor.lastrowid

    cursor.execute("SELECT @@IDENTITY")
    row = cursor.fetchone()
    return int(row[0]) if row else None


# ============================================================================
# FILE SYSTEM UTILITIES
# ============================================================================

def ensure_folders():
    """Tạo thư mục lưu file nếu chưa tồn tại"""
    try:
        os.makedirs(BORROW_FOLDER, exist_ok=True)
        os.makedirs(STUDENT_FOLDER, exist_ok=True)
        return True
    except Exception as e:
        print(f"Warning: Cannot create folders at {APP_FOLDER}: {e}")
        return False


def sanitize_filename(value: str) -> str:
    """Loại bỏ ký tự không hợp lệ khi tạo tên file"""
    safe = "".join(ch for ch in value if ch.isalnum() or ch in " _-.")
    return safe.strip().replace(" ", "_")


def get_borrow_file_path(borrow_id: int, borrower_name: str) -> str:
    """Lấy đường dẫn file mượn sách"""
    sanitized_name = sanitize_filename(borrower_name)
    filename = f"borrow_{borrow_id}_{sanitized_name}.txt"
    return os.path.join(BORROW_FOLDER, filename)


def get_student_file_path(ma_hs: str) -> str:
    """Lấy đường dẫn file thông tin học sinh"""
    sanitized_id = sanitize_filename(ma_hs)
    filename = f"student_{sanitized_id}.txt"
    return os.path.join(STUDENT_FOLDER, filename)


def create_student_file(ho_va_ten: str, lop: str, ma_hs: str, ngay_sinh: datetime.date):
    """Tạo file thông tin khi thêm học sinh"""
    if not ensure_folders():
        return None
    try:
        path = get_student_file_path(ma_hs)
        with open(path, "w", encoding="utf-8") as f:
            f.write("THONG TIN HOC SINH\n")
            f.write("=" * 40 + "\n")
            f.write(f"Ho va ten: {ho_va_ten}\n")
            f.write(f"Lop: {lop}\n")
            f.write(f"Ma HS: {ma_hs}\n")
            f.write(f"Ngay sinh: {ngay_sinh}\n")
            f.write(f"Ngay tao: {datetime.datetime.now()}\n")
        return path
    except Exception as e:
        print(f"Error creating student file: {e}")
        return None


def create_borrow_file(borrow_id: int, borrower_name: str, borrower_token: str, 
                       book_code: str, borrow_date: datetime.date, return_date: str):
    """Tạo file thông tin mượn sách khi người dùng nhập tên"""
    if not ensure_folders():
        return None
    try:
        path = get_borrow_file_path(borrow_id, borrower_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write("THONG TIN MUON SACH\n")
            f.write("=" * 40 + "\n")
            f.write(f"ID Phieu Muon: {borrow_id}\n")
            f.write(f"Ho va ten: {borrower_name}\n")
            f.write(f"Ma hoc sinh: {borrower_token}\n")
            f.write(f"Ma sach: {book_code}\n")
            f.write(f"Ngay muon: {borrow_date}\n")
            f.write(f"Ngay tra du kien: {return_date or 'Khong co'}\n")
            f.write(f"Ngay tao file: {datetime.datetime.now()}\n")
        return path
    except Exception as e:
        print(f"Error creating borrow file: {e}")
        return None


def delete_borrow_file(borrow_id: int, borrower_name: str):
    """Xóa file mượn khi trả sách"""
    path = get_borrow_file_path(borrow_id, borrower_name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def delete_student_file(ma_hs: str):
    """Xóa file học sinh"""
    path = get_student_file_path(ma_hs)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


# ============================================================================
# DATABASE SCHEMA MANAGEMENT
# ============================================================================

def get_table_names(cursor):
    """Liệt kê tất cả các bảng trong cơ sở dữ liệu"""
    if USE_SQLITE:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

    tables = []
    for row in cursor.tables(tableType='TABLE'):
        tables.append(row.table_name)
    return tables


def get_table_columns(cursor, table_name):
    """Liệt kê các cột của một bảng"""
    try:
        if USE_SQLITE:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            return [row[1] for row in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM [{table_name}] WHERE 1=0")
        columns = [column[0] for column in cursor.description]
        return columns
    except Exception:
        return []


def ensure_tables(cursor):
    """Kiểm tra và tạo các bảng cần thiết"""
    existing_tables = [table.upper() for table in get_table_names(cursor)]
    
    if BORROWER_TABLE.upper() not in existing_tables:
        if USE_SQLITE:
            cursor.execute(
                f'CREATE TABLE "{BORROWER_TABLE}" ('
                f'"Mã HS" TEXT,'
                f'"họ và tên" TEXT,'
                f'"lớp" TEXT,'
                f'"ngày sinh" DATE'
                f')'
            )
        else:
            cursor.execute(
                f"CREATE TABLE [{BORROWER_TABLE}] ("
                f"[Mã HS] TEXT(50),"
                f"[họ và tên] TEXT(255),"
                f"[lớp] TEXT(50),"
                f"[ngày sinh] DATE"
                f")"
            )
        cursor.connection.commit()
        print(f"✓ Đã tạo bảng: {BORROWER_TABLE}")

    if BOOK_TABLE.upper() not in existing_tables:
        if USE_SQLITE:
            cursor.execute(
                f'CREATE TABLE "{BOOK_TABLE}" ('
                f'"ID" INTEGER PRIMARY KEY AUTOINCREMENT,'
                f'"tên sách" TEXT,'
                f'"TÁC GIẢ" TEXT,'
                f'"mã sách" TEXT,'
                f'"TOKEN SÁCH" TEXT'
                f')'
            )
        else:
            cursor.execute(
                f"CREATE TABLE [{BOOK_TABLE}] ("
                f"[ID] AUTOINCREMENT PRIMARY KEY,"
                f"[tên sách] TEXT(255),"
                f"[TÁC GIẢ] TEXT(255),"
                f"[mã sách] TEXT(50),"
                f"[TOKEN SÁCH] TEXT(50)"
                f")"
            )
        cursor.connection.commit()
        print(f"✓ Đã tạo bảng: {BOOK_TABLE}")

    if BORROWING_RETURNING_TABLE.upper() not in existing_tables:
        if USE_SQLITE:
            cursor.execute(
                f'CREATE TABLE "{BORROWING_RETURNING_TABLE}" ('
                f'"ID" INTEGER PRIMARY KEY AUTOINCREMENT,'
                f'"NGÀY MƯỢM" DATE,'
                f'"TOKEN NGÀY MƯỢM" TEXT,'
                f'"TOKEN NGÀY TRẢ" TEXT,'
                f'"NGÀY TRẢ DỰ KIẾN" DATE,'
                f'"NGÀY TRẢ" DATE'
                f')'
            )
        else:
            cursor.execute(
                f"CREATE TABLE [{BORROWING_RETURNING_TABLE}] ("
                f"[ID] AUTOINCREMENT PRIMARY KEY,"
                f"[NGÀY MƯỢM] DATE,"
                f"[TOKEN NGÀY MƯỢM] TEXT(50),"
                f"[TOKEN NGÀY TRẢ] TEXT(50),"
                f"[NGÀY TRẢ DỰ KIẾN] DATE,"
                f"[NGÀY TRẢ] DATE"
                f")"
            )
        cursor.connection.commit()
        print(f"✓ Đã tạo bảng: {BORROWING_RETURNING_TABLE}")


def inspect_database():
    """Kiểm tra cấu trúc cơ sở dữ liệu"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("\n" + "=" * 60)
        print("DATABASE SCHEMA INSPECTION")
        print("=" * 60)
        
        tables = get_table_names(cursor)
        print(f"\nTổng số bảng: {len(tables)}\n")
        
        for table_name in tables:
            print(f"TABLE: {table_name}")
            columns = get_table_columns(cursor, table_name)
            for col in columns:
                print(f"  - {col}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Lỗi khi kiểm tra cơ sở dữ liệu: {e}")


# ============================================================================
# BORROWER MANAGEMENT
# ============================================================================

def find_borrowers_by_name(cursor, borrower_name: str):
    """Tìm học sinh theo tên"""
    cursor.execute(
        f"SELECT [Mã HS], [họ và tên], [lớp] FROM [{BORROWER_TABLE}] WHERE [họ và tên] = ?",
        (borrower_name,)
    )
    return cursor.fetchall()


def add_borrower(cursor, ho_va_ten: str, lop: str, ma_hs: str = None, ngay_sinh: datetime.date = None):
    """Thêm học sinh mới"""
    if ma_hs is None:
        ma_hs = generate_token()
    if ngay_sinh is None:
        ngay_sinh = datetime.date.today()

    cursor.execute(
        f"INSERT INTO [{BORROWER_TABLE}] ([họ và tên], [lớp], [Mã HS], [ngày sinh]) VALUES (?, ?, ?, ?)",
        (ho_va_ten, lop, ma_hs, ngay_sinh)
    )
    student_file = create_student_file(ho_va_ten, lop, ma_hs, ngay_sinh)
    return ma_hs, student_file


def choose_borrower(cursor, borrower_name: str):
    """Chọn học sinh nếu có nhiều người cùng tên"""
    rows = find_borrowers_by_name(cursor, borrower_name)
    if not rows:
        return None
    if len(rows) == 1:
        return rows[0]

    print("Có nhiều học sinh trùng tên. Chọn Mã HS:")
    for row in rows:
        print(f"- Mã HS: {row[0]}, Họ và tên: {row[1]}, Lớp: {row[2]}")
    selected = input("Nhập Mã HS: ").strip()
    for row in rows:
        if row[0] == selected:
            return row
    print("Không tìm thấy Mã HS phù hợp.")
    return None


# ============================================================================
# BOOK MANAGEMENT
# ============================================================================

def add_book(cursor, ten_sach: str, tac_gia: str, ma_sach: str = None):
    """Thêm sách mới"""
    if ma_sach is None:
        ma_sach = generate_token()
    cursor.execute(
        f"INSERT INTO [{BOOK_TABLE}] ([tên sách], [TÁC GIẢ], [mã sách], [TOKEN SÁCH]) VALUES (?, ?, ?, NULL)",
        (ten_sach, tac_gia, ma_sach)
    )
    return ma_sach


def get_book_by_code(cursor, book_code: str):
    """Tìm sách theo mã"""
    cursor.execute(
        f"SELECT [ID], [tên sách], [TÁC GIẢ], [mã sách], [TOKEN SÁCH] FROM [{BOOK_TABLE}] WHERE [mã sách] = ?",
        (book_code,)
    )
    return cursor.fetchone()


def get_available_books(cursor):
    """Lấy sách khả dụng hiện tại"""
    cursor.execute(f"SELECT [ID], [tên sách], [TÁC GIẢ], [mã sách], [TOKEN SÁCH] FROM [{BOOK_TABLE}] WHERE [TOKEN SÁCH] IS NULL OR [TOKEN SÁCH] = ''")
    return cursor.fetchall()


def get_all_books(cursor):
    """Lấy tất cả sách"""
    cursor.execute(f"SELECT [ID], [tên sách], [TÁC GIẢ], [mã sách], [TOKEN SÁCH] FROM [{BOOK_TABLE}]")
    return cursor.fetchall()


def get_book_by_id(cursor, book_id: int):
    """Tìm sách theo ID"""
    cursor.execute(
        f"SELECT [ID], [tên sách], [TÁC GIẢ], [mã sách], [TOKEN SÁCH] FROM [{BOOK_TABLE}] WHERE [ID] = ?",
        (book_id,)
    )
    return cursor.fetchone()


def show_books(cursor, only_available: bool = False):
    """Hiển thị sách trong một hộp lựa chọn"""
    books = get_available_books(cursor) if only_available else get_all_books(cursor)
    if not books:
        print("Không có sách.")
        return []

    title = "Sách khả dụng" if only_available else "Tất cả sách"
    headers = ["ID", "Tên sách", "Tác giả", "Mã sách", "Trạng thái"]
    rows = []
    for book in books:
        status = "Khả dụng" if book[4] in (None, "") else "Đã mượn"
        rows.append([str(book[0]), book[1] or "", book[2] or "", book[3] or "", status])

    widths = [len(headers[i]) for i in range(len(headers))]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    separator = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_row = "|" + "|".join(f" {headers[i].ljust(widths[i])} " for i in range(len(headers))) + "|"
    inner_width = len(separator) - 4

    print(f"\n{separator}")
    print(f"| {title.center(inner_width)} |")
    print(separator)
    print(header_row)
    print(separator)
    for row in rows:
        print("|" + "|".join(f" {row[i].ljust(widths[i])} " for i in range(len(row))) + "|")
    print(separator)
    print()
    return books


def get_student_borrow_status(cursor):
    """Lấy bảng học sinh đã mượn hoặc đã trả sách."""
    query = (
        f"SELECT b.[họ và tên], b.[lớp], b.[Mã HS], br.[ID], br.[NGÀY MƯỢM], br.[NGÀY TRẢ], br.[TOKEN NGÀY TRẢ], bk.[tên sách], bk.[mã sách] "
        f"FROM [{BORROWER_TABLE}] b "
        f"LEFT JOIN [{BORROWING_RETURNING_TABLE}] br ON b.[Mã HS] = br.[TOKEN NGÀY MƯỢM] "
        f"LEFT JOIN [{BOOK_TABLE}] bk ON br.[TOKEN NGÀY TRẢ] = bk.[mã sách] "
        f"WHERE br.[ID] IS NOT NULL "
        f"ORDER BY b.[họ và tên], br.[ID]"
    )
    cursor.execute(query)
    return cursor.fetchall()


def display_student_borrow_table(cursor):
    """Hiển thị bảng học sinh đã mượn/trả sách."""
    data = get_student_borrow_status(cursor)
    if not data:
        print("Không có học sinh nào đã mượn hoặc trả sách.")
        return

    headers = ["Họ và tên", "Lớp", "Mã HS", "ID Mượn", "Ngày mượn", "Ngày trả", "Sách", "Mã sách", "Trạng thái"]
    rows = []
    for row in data:
        status = "Trả" if row[5] is not None else "Đang mượn"
        rows.append([
            row[0] or "",
            row[1] or "",
            row[2] or "",
            str(row[3]) if row[3] is not None else "",
            str(row[4]) if row[4] is not None else "",
            str(row[5]) if row[5] is not None else "",
            row[7] or "",
            row[8] or "",
            status,
        ])

    widths = [len(headers[i]) for i in range(len(headers))]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    separator = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_row = "|" + "|".join(f" {headers[i].ljust(widths[i])} " for i in range(len(headers))) + "|"
    inner_width = len(separator) - 4

    print(f"\n{separator}")
    print(f"| {'BẢNG HỌC SINH MƯỢN/TRẢ'.center(inner_width)} |")
    print(separator)
    print(header_row)
    print(separator)
    for row in rows:
        print("|" + "|".join(f" {row[i].ljust(widths[i])} " for i in range(len(row))) + "|")
    print(separator)
    print()


# ============================================================================
# BORROWING/RETURNING OPERATIONS
# ============================================================================

def borrow_book(cursor, borrower_token: str, book_code: str, 
                borrow_date: datetime.date, return_date):
    """Tạo bản ghi mượn và đánh dấu sách đã bị mượn"""
    cursor.execute(
        f"INSERT INTO [{BORROWING_RETURNING_TABLE}] ([NGÀY MƯỢM], [TOKEN NGÀY MƯỢM], [TOKEN NGÀY TRẢ], [NGÀY TRẢ DỰ KIẾN], [NGÀY TRẢ]) VALUES (?, ?, ?, ?, ?)",
        (borrow_date, borrower_token, book_code, return_date, None)
    )
    borrow_id = get_last_insert_id(cursor)
    cursor.execute(
        f"UPDATE [{BOOK_TABLE}] SET [TOKEN SÁCH] = ? WHERE [mã sách] = ?",
        (borrower_token, book_code)
    )
    return borrow_id


def find_active_borrow_by_name(cursor, borrower_name: str):
    """Tìm phiếu mượn đang mở theo tên học sinh"""
    query = (
        f"SELECT br.[ID], b.[họ và tên], br.[TOKEN NGÀY MƯỢM], br.[TOKEN NGÀY TRẢ], br.[NGÀY MƯỢM], br.[NGÀY TRẢ DỰ KIẾN] "
        f"FROM [{BORROWING_RETURNING_TABLE}] br "
        f"JOIN [{BORROWER_TABLE}] b ON b.[Mã HS] = br.[TOKEN NGÀY MƯỢM] "
        f"WHERE b.[họ và tên] = ? AND br.[NGÀY TRẢ] IS NULL"
    )
    cursor.execute(query, (borrower_name,))
    return cursor.fetchall()


def return_book(cursor, borrow_id: int):
    """Trả sách: cập nhật ngày trả và giải phóng sách"""
    today = datetime.date.today()
    cursor.execute(
        f"SELECT [TOKEN NGÀY TRẢ], [TOKEN NGÀY MƯỢM] FROM [{BORROWING_RETURNING_TABLE}] WHERE [ID] = ?",
        (borrow_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Không tìm thấy bản ghi mượn với ID {borrow_id}")

    book_code, borrower_token = row
    cursor.execute(
        f"UPDATE [{BORROWING_RETURNING_TABLE}] SET [NGÀY TRẢ] = ? WHERE [ID] = ?",
        (today, borrow_id)
    )
    cursor.execute(
        f"UPDATE [{BOOK_TABLE}] SET [TOKEN SÁCH] = NULL WHERE [mã sách] = ?",
        (book_code,)
    )

    cursor.execute(
        f"SELECT [họ và tên] FROM [{BORROWER_TABLE}] WHERE [Mã HS] = ?",
        (borrower_token,)
    )
    row = cursor.fetchone()
    borrower_name = row[0] if row else ""
    deleted = delete_borrow_file(borrow_id, borrower_name)
    return book_code, borrower_name, deleted


# ============================================================================
# INPUT UTILITIES
# ============================================================================

def prompt_date(text: str, allow_empty: bool = False):
    """Yêu cầu nhập ngày"""
    while True:
        value = input(text).strip()
        if allow_empty and value == "":
            return None
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            print("Định dạng sai. Vui lòng nhập YYYY-MM-DD hoặc để trống.")


# ============================================================================
# REPORTING
# ============================================================================

def get_linked_data(cursor):
    """Lấy dữ liệu liên kết từ tất cả bảng"""
    query = (
        f"SELECT b.[họ và tên], b.[lớp], b.[Mã HS], br.[ID], br.[NGÀY MƯỢM], br.[NGÀY TRẢ], br.[TOKEN NGÀY TRẢ], "
        f"bk.[tên sách], bk.[TÁC GIẢ], bk.[mã sách] "
        f"FROM [{BORROWER_TABLE}] b "
        f"LEFT JOIN [{BORROWING_RETURNING_TABLE}] br ON b.[Mã HS] = br.[TOKEN NGÀY MƯỢM] "
        f"LEFT JOIN [{BOOK_TABLE}] bk ON br.[TOKEN NGÀY TRẢ] = bk.[mã sách]"
    )
    cursor.execute(query)
    return cursor.fetchall()


def display_linked_data(cursor):
    """Hiển thị dữ liệu liên kết"""
    data = get_linked_data(cursor)
    if not data:
        print("Không có dữ liệu.")
        return
    
    print("\nDỮ LIỆU LIÊN KẾT:")
    print("-" * 80)
    for row in data:
        print(f"Học sinh: {row[0]} ({row[2]}) - Lớp: {row[1]}")
        if row[3]:
            print(f"  ID Mượn: {row[3]} - Sách: {row[7]} ({row[8]})")
            print(f"  Ngày mượn: {row[4]} - Ngày trả: {row[5]}")
        print()


# ============================================================================
# MAIN MENU SYSTEM
# ============================================================================

def print_ascii_banner():
    """In banner ASCII với tên tác giả"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║          ASCII LIBRARY MANAGEMENT TOOL (ASCLL) v1.0          ║
    ║                                                               ║
    ║              Công cụ Quản lý Thư viện Tích hợp              ║
    ║                                                               ║
    ║                 ██████╗ ███████╗██╗   ██╗███╗   ███╗        ║
    ║                 ██╔══██╗██╔════╝██║   ██║████╗ ████║        ║
    ║                 ██████╔╝█████╗  ██║   ██║██╔████╔██║        ║
    ║                 ██╔══██╗██╔══╝  ╚██╗ ██╔╝██║╚██╔╝██║        ║
    ║                 ██║  ██║███████╗ ╚████╔╝ ██║ ╚═╝ ██║        ║
    ║                 ╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚═╝     ╚═╝        ║
    ║                                                               ║
    ║                 Developed by Khanh 2007                      ║
    ║                                                               ║
    ║            Database: SQLite (Cross-platform Ready)           ║
    ║            Storage: ~/.ascii_library (Portable)              ║
    ║            Platform: Windows | Linux | Android               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main_menu():
    """Menu chính"""
    ensure_folders()
    print_ascii_banner()
    try:
        if not USE_SQLITE and not os.path.isfile(DB_FILE):
            raise FileNotFoundError(f"Không tìm thấy cơ sở dữ liệu Access: {DB_FILE}")

        conn = get_connection()
        cursor = conn.cursor()
        ensure_tables(cursor)

        while True:
            print("\n" + "=" * 60)
            print("ASCII LIBRARY MANAGEMENT TOOL - ASCLL")
            print("Công cụ Quản lý Thư viện")
            print("=" * 60)
            print("1. Thêm học sinh")
            print("2. Thêm sách")
            print("3. Mượn sách theo tên học sinh")
            print("4. Trả sách")
            print("5. Hiển thị sách và chọn sách")
            print("6. Liệt kê sách khả dụng")
            print("7. Liệt kê các phiếu mượn đang mở")
            print("8. Bảng học sinh đã mượn/trả")
            print("9. Xem dữ liệu liên kết")
            print("10. Kiểm tra cấu trúc cơ sở dữ liệu")
            print("11. Thoát")
            print("-" * 60)
            choice = input("Chọn chức năng (1-11): ").strip()

            if choice == '1':
                print("\n--- THEM HOC SINH ---")
                try:
                    ho_va_ten = input("Ho va ten: ").strip()
                    lop = input("Lop: ").strip()
                    ngay_sinh = prompt_date("Ngay sinh (YYYY-MM-DD) hoac de trong: ", allow_empty=True)
                    ma_hs, student_file = add_borrower(cursor, ho_va_ten, lop, ngay_sinh=ngay_sinh)
                    conn.commit()
                    print(f"Success: Da them hoc sinh: {ho_va_ten}")
                    print(f"  Ma HS: {ma_hs}")
                    if student_file:
                        print(f"  File: {student_file}")
                    else:
                        print(f"  Warning: Could not create student file at {STUDENT_FOLDER}")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == '2':
                print("\n--- THEM SACH ---")
                try:
                    ten_sach = input("Ten sach: ").strip()
                    tac_gia = input("Tac gia: ").strip()
                    ma_sach = add_book(cursor, ten_sach, tac_gia)
                    conn.commit()
                    print(f"Success: Da them sach: {ten_sach}")
                    print(f"  Ma sach: {ma_sach}")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == '3':
                print("\n--- MUON SACH ---")
                try:
                    borrower_name = input("Nhap ten hoc sinh muon sach: ").strip()
                    borrower = choose_borrower(cursor, borrower_name)
                    if not borrower:
                        print("Khong tim thay hoc sinh voi ten da nhap.")
                        continue
                    book_code = input("Ma sach: ").strip()
                    book = get_book_by_code(cursor, book_code)
                    if not book:
                        print("Khong tim thay sach voi Ma sach do.")
                        continue
                    if book[4] not in (None, ""):
                        print("Sach hien khong kha dung.")
                        continue
                    borrow_date = prompt_date("Ngay muon (YYYY-MM-DD) hoac de trong: ", allow_empty=True) or datetime.date.today()
                    return_date = prompt_date("Ngay tra du kien (YYYY-MM-DD) hoac de trong: ", allow_empty=True)
                    borrow_id = borrow_book(cursor, borrower[0], book_code, borrow_date, return_date)
                    conn.commit()
                    borrow_file = create_borrow_file(borrow_id, borrower[1], borrower[0], book_code, borrow_date, str(return_date) if return_date else "")
                    print(f"Success: Da muon sach thanh cong")
                    print(f"  ID muon: {borrow_id}")
                    if borrow_file:
                        print(f"  File: {borrow_file}")
                    else:
                        print(f"  Warning: Could not create borrow file at {BORROW_FOLDER}")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == '4':
                print("\n--- TRA SACH ---")
                try:
                    borrower_name = input("Nhap ten hoc sinh tra sach hoac de trong de dung ID muon: ").strip()
                    borrow_id = None
                    if borrower_name:
                        active = find_active_borrow_by_name(cursor, borrower_name)
                        if not active:
                            print("Khong tim thay phieu muon dang mo cho hoc sinh nay.")
                            continue
                        if len(active) > 1:
                            print("Co nhieu phieu muon dang mo:")
                            for row in active:
                                print(f"- ID: {row[0]}, Ma sach: {row[3]}, Ngay muon: {row[4]}, Ngay tra du kien: {row[5]}")
                            borrow_id = int(input("Nhap ID muon de tra: ").strip())
                        else:
                            borrow_id = active[0][0]
                    else:
                        borrow_id = int(input("Nhap ID muon: ").strip())

                    book_code, borrower_name, deleted = return_book(cursor, borrow_id)
                    conn.commit()
                    print(f"Success: Da tra sach thanh cong")
                    print(f"  Ma sach: {book_code}")
                    print(f"  Hoc sinh: {borrower_name}")
                    if deleted:
                        print("  File muon da bi xoa.")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == '5':
                print("\n--- HIỂN THỊ SÁCH ---")
                books = show_books(cursor)
                if books:
                    selected = input("Nhập ID hoặc Mã sách để xem chi tiết, hoặc Enter để quay lại: ").strip()
                    if selected:
                        book = None
                        if selected.isdigit():
                            try:
                                book_id = int(selected)
                                book = get_book_by_id(cursor, book_id)
                            except ValueError:
                                book = None
                        if book is None:
                            book = get_book_by_code(cursor, selected)
                        if book:
                            status = "Khả dụng" if book[4] in (None, "") else "Đã mượn"
                            print("\n--- CHI TIẾT SÁCH ---")
                            print(f"ID: {book[0]}")
                            print(f"Tên sách: {book[1]}")
                            print(f"Tác giả: {book[2]}")
                            print(f"Mã sách: {book[3]}")
                            print(f"Trạng thái: {status}")
                        else:
                            print("Không tìm thấy sách tương ứng.")

            elif choice == '6':
                print("\n--- SÁCH KHẢ DỤNG ---")
                books = get_available_books(cursor)
                if not books:
                    print("Không có sách khả dụng.")
                else:
                    print(f"Tổng sách khả dụng: {len(books)}\n")
                    for book in books:
                        print(f"- ID: {book[0]}")
                        print(f"  Tên: {book[1]}")
                        print(f"  Tác giả: {book[2]}")
                        print(f"  Mã sách: {book[3]}")
                        print()

            elif choice == '7':
                print("\n--- PHIẾU MƯỢN ĐANG MỞ ---")
                cursor.execute(
                    f"SELECT br.[ID], b.[họ và tên], br.[TOKEN NGÀY MƯỢM], br.[TOKEN NGÀY TRẢ], br.[NGÀY MƯỢM], br.[NGÀY TRẢ DỰ KIẾN] "
                    f"FROM [{BORROWING_RETURNING_TABLE}] br "
                    f"JOIN [{BORROWER_TABLE}] b ON b.[Mã HS] = br.[TOKEN NGÀY MƯỢM] "
                    f"WHERE br.[NGÀY TRẢ] IS NULL"
                )
                rows = cursor.fetchall()
                if not rows:
                    print("Không có phiếu mượn đang mở.")
                else:
                    print(f"Tổng phiếu mượn đang mở: {len(rows)}\n")
                    for row in rows:
                        print(f"- ID: {row[0]}")
                        print(f"  Học sinh: {row[1]}")
                        print(f"  Mã HS: {row[2]}")
                        print(f"  Mã sách: {row[3]}")
                        print(f"  Ngày mượn: {row[4]}")
                        print(f"  Ngày trả dự kiến: {row[5]}")
                        print()

            elif choice == '8':
                display_student_borrow_table(cursor)

            elif choice == '9':
                print("\n--- DỮ LIỆU LIÊN KẾT ---")
                display_linked_data(cursor)

            elif choice == '10':
                print("\n--- KIỂM TRA CẤU TRÚC CƠ SỞ DỮ LIỆU ---")
                inspect_database()

            elif choice == '11':
                break

            else:
                print("Lựa chọn không hợp lệ. Vui lòng thử lại.")

        cursor.close()
        conn.close()
        print("\n✓ Kết thúc chương trình.")

    except Exception as e:
        print(f"✗ Lỗi: {e}")


if __name__ == "__main__":
    main_menu()
