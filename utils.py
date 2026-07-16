import pandas as pd
import difflib
import re
from pathlib import Path
import io

def auto_map_columns(df):
    """تشخیص هوشمند ستون‌ها"""
    columns = df.columns.tolist()
    clean_columns = {col: re.sub(r'\s+', ' ', col.strip()).lower() for col in columns}

    keywords = {
        'date': ['date', 'day', 'تاریخ', 'زمان', 'time', 'روز'],
        'cost': ['cost', 'spend', 'amount', 'هزینه', 'قیمت', 'expense', 'budget'],
        'conversions': ['conversions', 'sales', 'purchases', 'خرید', 'تبدیل', 'orders']
    }

    found = {}
    suggestions = {}

    for role, kw_list in keywords.items():
        # جستجوی دقیق
        exact_matches = [col for col in columns if clean_columns.get(col) in [k.lower() for k in kw_list]]
        if exact_matches:
            found[role] = exact_matches[0]
            continue

        # جستجوی تقریبی
        all_matches = []
        for col in columns:
            for kw in kw_list:
                score = difflib.SequenceMatcher(None, clean_columns.get(col, ''), kw.lower()).ratio()
                if score >= 0.75:
                    all_matches.append((col, score))
        
        if all_matches:
            best = max(all_matches, key=lambda x: x[1])
            found[role] = best[0]
        else:
            found[role] = None
            suggestions[role] = sorted(
                [(col, max(difflib.SequenceMatcher(None, clean_columns.get(col, ''), kw.lower()).ratio() for kw in kw_list))
                 for col in columns], 
                key=lambda x: x[1], reverse=True
            )[:5]

    return found, suggestions, columns


def load_and_standardize(file_input, manual_mapping=None):
    """فایل را خوانده و استاندارد می‌کند"""
    try:
        if hasattr(file_input, 'getvalue'):  # UploadedFile
            file_bytes = file_input.getvalue()
            file_name = file_input.name
            if file_name.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8-sig')
            else:
                engine = 'openpyxl' if file_name.endswith('.xlsx') else 'xlrd'
                df = pd.read_excel(io.BytesIO(file_bytes), engine=engine)
        else:
            file_path = Path(file_input)
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path, encoding='utf-8-sig')

        if df.empty:
            raise ValueError("فایل خالی است.")

        if manual_mapping:
            date_col = manual_mapping['date']
            cost_col = manual_mapping['cost']
            conv_col = manual_mapping['conversions']
        else:
            found, suggestions, columns = auto_map_columns(df)
            missing = [role for role, col in found.items() if col is None]
            if missing:
                error_msg = "ستون‌های زیر تشخیص داده نشد:\n"
                for role in missing:
                    error_msg += f"• {role}: {[c for c,_ in suggestions.get(role, [])]}\n"
                raise ValueError(error_msg)
            
            date_col = found['date']
            cost_col = found['cost']
            conv_col = found['conversions']

        df_std = pd.DataFrame({
            'date': pd.to_datetime(df[date_col], errors='coerce'),
            'cost': pd.to_numeric(df[cost_col], errors='coerce'),
            'conversions': pd.to_numeric(df[conv_col], errors='coerce').round().astype('Int64')
        })

        df_std = df_std.dropna(subset=['date']).reset_index(drop=True)
        return df_std

    except Exception as e:
        raise ValueError(f"خطا: {str(e)}")
