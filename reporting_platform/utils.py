def calc_level(report_count):
    if report_count >= 50:
        return 'خبير 🔥'
    elif report_count >= 20:
        return 'مساهم نشط 💪'
    elif report_count >= 5:
        return 'مشارك 🤝'
    else:
        return 'مبتدئ 🐣'
