import pandas as pd
import difflib
import re
from pathlib import Path

def load_and_standardize(file_path, column_mapping=None):
    try:
        file_path = Path(file_path)
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, engine='openpyxl' if file_path.suffix == '.xlsx' else 'xlrd')
        elif file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        else:
            raise ValueError("فرمت فایل پشتیبانی نمی‌شود.")
    except Exception as e:
        raise ValueError(f"خطا در خواندن فایل: {e}")

    if df.empty:
        raise ValueError("فایل خالی است.")

    columns = df.columns.tolist()
    clean_columns = {col: re.sub(r'\s+', ' ', col.strip()).lower() for col in columns}

    if column_mapping is not None:
        missing = [role for role, col in column_mapping.items() if col not in columns]
        if missing:
            raise ValueError(f"ستون‌های معرفی‌شده وجود ندارند: {missing}")
        date_col = column_mapping['date']
        cost_col = column_mapping['cost']
        conv_col = column_mapping['conversions']
    else:
        keywords = {
            'date': ['date', 'day', 'تاریخ', 'زمان', 'time', 'روز'],
            'cost': ['cost', 'spend', 'amount', 'هزینه', 'قیمت', 'expense', 'budget'],
            'conversions': ['conversions', 'sales', 'purchases', 'خرید', 'تبدیل', 'orders', 'transactions']
        }
        found = {}
        for role, kw_list in keywords.items():
            exact_matches = [col for col in columns if clean_columns[col] in kw_list]
            if exact_matches:
                found[role] = exact_matches[0]
            else:
                all_matches = []
                for col in columns:
                    for kw in kw_list:
                        score = difflib.SequenceMatcher(None, clean_columns[col], kw).ratio()
                        if score >= 0.8:
                            all_matches.append((col, score))
                if all_matches:
                    best = max(all_matches, key=lambda x: x[1])
                    found[role] = best[0]
                else:
                    found[role] = None

        date_col = found.get('date')
        cost_col = found.get('cost')
        conv_col = found.get('conversions')

        missing_roles = [role for role, col in found.items() if col is None]
        if missing_roles:
            suggestions = {}
            for role in missing_roles:
                kw_list = keywords[role]
                suggestions[role] = []
                for col in columns:
                    for kw in kw_list:
                        score = difflib.SequenceMatcher(None, clean_columns[col], kw).ratio()
                        if score >= 0.6:
                            suggestions[role].append((col, score))
                suggestions[role].sort(key=lambda x: x[1], reverse=True)
                suggestions[role] = [col for col, _ in suggestions[role][:3]]

            error_msg = f"عدم تشخیص ستون‌ها.\nستون‌های موجود: {columns}\nپیشنهادات:\n"
            for role, cols in suggestions.items():
                error_msg += f"  - {role}: {cols if cols else 'هیچ پیشنهادی'}\n"
            raise ValueError(error_msg)

    try:
        date_series = pd.to_datetime(df[date_col], errors='coerce')
        if date_series.isna().all():
            raise ValueError(f"ستون '{date_col}' تاریخ معتبر ندارد.")
        cost_series = pd.to_numeric(df[cost_col], errors='coerce')
        if cost_series.isna().all():
            raise ValueError(f"ستون '{cost_col}' عدد معتبر ندارد.")
        conv_series = pd.to_numeric(df[conv_col], errors='coerce')
        if conv_series.isna().all():
            raise ValueError(f"ستون '{conv_col}' عدد معتبر ندارد.")
        conv_series = conv_series.round().astype('Int64')
    except Exception as e:
        raise ValueError(f"خطا در تبدیل داده: {e}")

    result_df = pd.DataFrame({
        'date': date_series,
        'cost': cost_series.astype(float),
        'conversions': conv_series
    })
    result_df = result_df.dropna(subset=['date'])
    return result_df
