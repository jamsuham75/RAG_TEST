#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한글이 완벽하게 포함된 manual.pdf 생성 스크립트
Windows 환경에서 실행하세요!

필요한 라이브러리:
pip install reportlab pillow
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys

# ✨ Windows 시스템 폰트 등록
# 여러 폰트 옵션 시도 (맑은 고딕, 굴림, 궁서체)
font_paths = [
    "C:\\Windows\\Fonts\\malgun.ttf",      # 맑은 고딕
    "C:\\Windows\\Fonts\\gulim.ttc",       # 굴림
    "C:\\Windows\\Fonts\\arial.ttf",       # Arial (영문용)
]

font_name = None
for font_path in font_paths:
    if os.path.exists(font_path):
        try:
            if font_path.endswith('.ttc'):
                # TTC 파일은 특별 처리 필요
                pdfmetrics.registerFont(TTFont('KoreanFont', font_path, subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
            font_name = 'KoreanFont'
            print(f"✅ 폰트 등록 성공: {font_path}")
            break
        except Exception as e:
            print(f"⚠️  폰트 등록 실패: {font_path} - {e}")
            continue

if not font_name:
    print("❌ 한글 폰트를 찾을 수 없습니다!")
    print("   C:\\Windows\\Fonts\\에서 .ttf 파일을 확인하세요")
    sys.exit(1)

# 콘텐츠 정의
content = [
    ("제품 사용 설명서", 24, True),
    ("가정용 공기청정기 AP-3300", 14, True),
    ("", 6, False),
    
    ("목차", 14, True),
    ("1. 제품 개요", 11, False),
    ("2. 설치 방법", 11, False),
    ("3. 사용 방법", 11, False),
    ("4. 환불 및 교환 규정", 11, False),
    ("5. 보증 및 무상 A/S", 11, False),
    ("6. 문제 해결(FAQ)", 11, False),
    ("7. 고객센터 안내", 11, False),
    ("8. 제품 사양", 11, False),
    ("9. 품질보증서", 11, False),
    ("", 6, False),
    
    ("1. 제품 개요", 14, True),
    ("본 제품은 가정용 공기청정기로서, 초미세먼지·유해가스·생활 악취를 효과적으로 제거합니다.", 11, False),
    ("HEPA 13 등급 필터와 활성탄 필터를 함께 사용하여 실내 공기질을 쾌적하게 유지합니다.", 11, False),
    ("권장 사용 면적은 33㎡ 이내이며, 저소음 설계로 취침 시에도 사용할 수 있습니다.", 11, False),
    ("", 6, False),
    
    ("2. 설치 방법", 14, True),
    ("벽면에서 30cm 이상 떨어진 곳에 제품을 설치해 주세요.", 11, False),
    ("바닥이 평평하고 통풍이 잘 되는 곳에 두시는 것이 좋습니다.", 11, False),
    ("전원 코드는 접지가 된 콘센트에 연결해 주세요.", 11, False),
    ("커튼이나 가구 등으로 흡입구·배출구가 가려지지 않도록 주의해 주세요.", 11, False),
    ("", 6, False),
    
    ("3. 사용 방법", 14, True),
    ("전원 버튼을 눌러 제품을 켜고, 원하는 풍량 단계(약/중/강/자동)를 선택하세요.", 11, False),
    ("자동 모드에서는 내장된 먼지 센서가 실내 공기질을 감지하여 풍량을 자동으로 조절합니다.", 11, False),
    ("필터 교체 알림 램프가 켜지면 필터를 확인해 주세요.", 11, False),
    ("", 6, False),
    
    ("4. 환불 및 교환 규정", 14, True),
    ("환불", 12, True),
    ("상품 수령 후 7 일 이내에 환불을 신청하실 수 있습니다.", 11, False),
    ("단순 변심의 경우 왕복 배송비는 고객 부담입니다.", 11, False),
    ("교환", 12, True),
    ("상품 불량의 경우 30 일 이내에 교환이 가능합니다.", 11, False),
    ("이 경우 배송비는 당사가 부담합니다.", 11, False),
    ("", 6, False),
    
    ("5. 보증 및 무상 A/S", 14, True),
    ("본 제품은 구매일로부터 1 년간 무상 A/S 를 제공합니다.", 11, False),
    ("단, 사용자의 과실로 인한 고장이나 임의 분해·개조로 인한 손상은 무상 보증 대상에서 제외됩니다.", 11, False),
    ("보증서와 구매 영수증을 함께 보관해 주세요.", 11, False),
    ("A/S 문의는 고객센터 또는 가까운 서비스센터를 통해 접수하실 수 있으며, 접수 후 영업일 기준 3~5 일 이내에 처리됩니다.", 11, False),
    ("필터 등 소모품은 무상 보증 대상이 아니며 별도로 구매하실 수 있습니다.", 11, False),
    ("", 6, False),
    
    ("6. 문제 해결(FAQ)", 14, True),
    ("Q. 전원이 켜지지 않아요.", 11, False),
    ("A. 전원 코드가 콘센트에 제대로 연결되어 있는지 확인해 주세요.", 11, False),
    ("Q. 이상한 냄새가 나요.", 11, False),
    ("A. 필터 교체 시기가 지났을 수 있습니다. 필터 상태를 확인해 주세요.", 11, False),
    ("Q. 소음이 심해요.", 11, False),
    ("A. 흡입구에 이물질이 끼어 있지 않은지 확인해 주세요.", 11, False),
    ("", 6, False),
    
    ("7. 고객센터 안내", 14, True),
    ("운영 시간은 평일 09:00 ~ 18:00 입니다.", 11, False),
    ("전화 1588-0000 / 이메일 help@example.com", 11, False),
    ("", 6, False),
    
    ("8. 제품 사양", 14, True),
    ("모델명: AP-3300", 11, False),
    ("정격전압: AC 220V 60Hz", 11, False),
    ("소비전력: 45W", 11, False),
    ("적용면적: 33㎡ 이내", 11, False),
    ("필터: HEPA 13 등급 + 활성탄 필터", 11, False),
    ("소음: 20 ~ 52dB", 11, False),
    ("크기(가로×세로×높이): 320 × 320 × 620mm", 11, False),
    ("무게: 6.8kg", 11, False),
    ("", 6, False),
    
    ("9. 품질보증서", 14, True),
    ("본 보증서는 제품 구매를 증명하는 서류이며, 무상 A/S 시 반드시 제시해 주세요.", 11, False),
    ("제품명: 가정용 공기청정기 AP-3300", 11, False),
    ("구매일자: ______________________", 11, False),
    ("구매처: ______________________", 11, False),
    ("본 제품은 한국소비자원의 소비자분쟁해결기준에 따라 보상해 드립니다.", 11, False),
]

# PDF 생성
pdf_path = "manual_cleaned.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)
width, height = A4

# 여백 설정
left_margin = 2 * cm
top_margin = 2 * cm
right_margin = 2 * cm
line_height = 0.5 * cm
y_pos = height - top_margin

# 콘텐츠 작성
for text, font_size, is_bold in content:
    if not text:
        # 스페이서
        y_pos -= font_size / 72 * 2.54
    else:
        # 폰트 설정
        if is_bold:
            # Bold 효과는 색상으로 표현
            c.setFont(font_name, font_size)
        else:
            c.setFont(font_name, font_size)
        
        # 텍스트 작성
        c.drawString(left_margin, y_pos, text)
        y_pos -= line_height
        
        # 페이지 바뀜 체크
        if y_pos < 2 * cm:
            c.showPage()
            y_pos = height - top_margin

# PDF 저장
c.save()
print(f"✅ PDF 생성 완료!")
print(f"   파일: {pdf_path}")
print(f"   위치: {os.path.abspath(pdf_path)}")
print(f"\n💾 이 파일을 당신의 RAG_TEST/data/manual.pdf로 옮기세요!")
