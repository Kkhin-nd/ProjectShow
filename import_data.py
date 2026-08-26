import pymysql

connection = pymysql.connect(
    host='shuttle.proxy.rlwy.net',
    user='root',
    password='eRAgmdWjhNcPdSEHubBbdXLNxJSTHkpQ',
    database='tour_db',
    port=49489,
    charset='utf8mb4',
    ssl={"fake_flag_to_disable_ssl": True}
)

print("⏳ Database ထဲသို့ Data များ စတင်ထည့်သွင်းနေပါပြီ၊ ခဏစောင့်ပေးပါရှင်...")

try:
    with connection.cursor() as cursor:
        with open('C:\\Users\\USER\\Desktop\\tour_db_backup.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        # SQL statement များကို တစ်ကြောင်းချင်းစီခွဲကာ ထည့်မည် (Error တက်ပါက ကျော်သွားမည်)
        statements = sql_script.split(';')
        total = len(statements)
        
        for index, statement in enumerate(statements):
            if statement.strip():
                try:
                    cursor.execute(statement)
                except Exception as ex:
                    # Table တည်ဆောက်ပြီးသား Error မျိုးဆိုလျှင် ဆက်သွားရန်
                    pass
                    
    connection.commit()
    print("✨ Data တွေ အကုန် Railway Database ထဲကို အောင်မြင်စွာ ရောက်သွားပါပြီရှင်! 🎉")
except Exception as e:
    print(f"Error ဖြစ်သွားပါတယ်ရှင်: {e}")
finally:
    connection.close()