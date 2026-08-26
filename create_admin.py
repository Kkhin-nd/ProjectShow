import os
import django

# Django settings ကို ချိတ်ဆက်ခြင်း
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings') # your_project_name နေရာမှာ ကိုယ့် project නာမည်ထည့်ပါ
django.setup()

from django.contrib.auth.models import User

# လိုချင်တဲ့ Admin Username နဲ့ Password ကို ဒီမှာ ပြောင်းထည့်နိုင်ပါတယ်
username = 'myadmin'
email = 'admin@example.com'
password = 'mypassword123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✨ Admin အကောင့် '{username}' ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီရှင်! 🎉")
else:
    print(f"⚠️ ဒီ Username ({username}) က ရှိပြီးသား ဖြစ်နေပါတယ်ရှင်။")