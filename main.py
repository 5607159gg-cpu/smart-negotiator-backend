import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

app = FastAPI()

# تفعيل السماح الكامل لتطبيق الفلوتر بالاتصال بدون حظر المتصفح
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 تم وضع مفتاح الـ API الخاص بك هنا بنجاح
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تجهيز عميل جوجل الذكي الحديث لعام 2026
client = genai.Client(api_key=GEMINI_API_KEY)

# هندسة الأوامر الصارمة (System Prompts) لتوجيه شخصية المستشار والمفاوض
PROMPT_SEARCH = (
    "أنت خبير محترف ومستشار سيبراني في فحص السلع ومقارنة الأسعار. "
    "يقوم المستخدم بطلب منتج معين، ومهمتك هي تقديم فحص ومقارنة في المتاجر الموثوقة عالمياً وعربياً (Amazon, Noon, eBay, Jumia, AliExpress). "
    "رتب الخيارات من الأفضل للأقل، واشرح للمستخدم هل الخصم حقيقي، وهل السعر جيد مقارنة بالسوق، وانصحه بوضوح بالشراء الآن أم الانتظار, بأسلوب خبير تقني رصين وواضح ومقنع."
)

PROMPT_LEGAL = (
    "أنت مستشار قانوني صارم وااحترافي متخصص في صياغة الشكاوى الرسمية لحماية المستهلك. "
    "بناءً على تفاصيل المشكلة والشركة المشكو في حقها، قم بصياغة شكوى رسمية قوية، منظمة، ورصينة. "
    "تجنب الألفاظ الهجومية أو المسيئة تماماً، واجعل النص يبدأ بديباجة رسمية (السيد رئيس جهاز حماية المستهلك...) "
    "ثم الوقائع، ثم الطلبات الواضحة والخطوات القانونية لزيادة احتمالية الحل السريع من خدمة العملاء وتصعيد الموقف باحترافية."
)

async def gemini_stream_generator(message: str, section_type: str):
    """هذه الدالة تفتح بث حقيقي مع سيرفرات جوجل وترسل الكلمات فور ولادتها"""
    system_instruction = PROMPT_SEARCH if section_type == "search" else PROMPT_LEGAL
    
    try:
        # استدعاء نموذج جيميناي السريع والقوي لدعم البث التدريجي
        response = client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            ),
        )
        
        # لف على الكلمات القادمة حياً من جوجل وإرسالها فوراً لتطبيق الفلوتر
        for chunk in response:
            if chunk.text:
                yield f"data: {chunk.text}\n\n"
                await asyncio.sleep(0.01)
                
    except Exception as e:
        yield "data: fallback_error\n\n"

@app.post("/chat/stream")
async def chat_stream(request: Request):
    """الرابط الرئيسي المثبت برقم الـ IP في تطبيق الفلوتر الأسطوري الخاص بك"""
    body = await request.json()
    user_message = body.get("message", "")
    section_type = body.get("type", "search")
    
    return StreamingResponse(
        gemini_stream_generator(user_message, section_type), 
        media_type="text/event-stream"
    )
