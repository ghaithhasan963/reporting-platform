from collections import Counter

def get_hot_zones(reports, precision=2):
    # تحديد المناطق الأعلى خطورة حسب كثافة البلاغات
    grouped = Counter((round(r.latitude, precision), round(r.longitude, precision)) for r in reports if r.latitude and r.longitude)
    return grouped

def format_heatmap_data(reports):
    # تجهيز بيانات HeatMap
    return [[r.latitude, r.longitude] for r in reports if r.latitude and r.longitude]

def create_alert_text(report):
    # نص تنبيه للمستخدمين القريبين
    return f"⚠️ بلاغ جديد من نوع {report.category} في منطقتك، راجع التفاصيل حالًا!"

def get_level(approved_count):
    # حساب رتبة المستخدم تلقائيًا
    if approved_count >= 50:
        return "خبير 🔥"
    elif approved_count >= 20:
        return "نشط 💪"
    elif approved_count >= 5:
        return "مشارك 🤝"
    else:
        return "جديد 🐣"
