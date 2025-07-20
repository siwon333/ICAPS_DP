from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from openai import OpenAI
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# OpenAI 클라이언트 설정
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
)

def home(request):
    return render(request, 'main/home.html') # home page

def issues(request):
    return render(request, 'main/issues.html') # health issues page

def order(request):
    if request.method == 'POST':
        # 주문 처리 로직
        pass
    return render(request, 'main/order.html') # How to order Jamu page

def info(request):
    return render(request, 'main/info.html') # Description of Jamu page

def waiting(request):
    return render(request, 'main/waiting.html') # Waiting page

def complete(request):
    return render(request, 'main/complete.html') # complete page

def chatbot(request):
    return render(request, 'main/chatbot.html') # Chatbot page

@csrf_exempt
def chatbot_api(request):
    """OpenAI GPT API 연결 챗봇 (v1.0+ 호환)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message.strip():
                return JsonResponse({
                    'response': '메시지를 입력해주세요.',
                    'status': 'error'
                }, status=400)
            
            # API 키 확인
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your-api-key-here':
                # API 키가 없으면 테스트용 응답 사용
                return chatbot_api_fallback_response(user_message)
            
            # 새로운 OpenAI v1.0+ API 호출 방식
            response = client.chat.completions.create(
                model="gpt-4",  # 또는 "gpt-4"
                messages=[
                    {
                        "role": "system", 
                        "content": """주어진 레시피와 재료만 사용하여 아래 조건을 모두 지켜 요리법을 작성해 주세요.

                        아래 명시된 재료만 사용할 것
                        
                        아래 명시된 조리 순서만 포함할 것
                        
                        절대 새로운 재료나 새로운 조리법, 도구를 추가하지 말 것
                        
                        순서나 단계, 재료 명칭은 아래와 정확히 일치시킬 것
                        
                        창의적 변형, 생략, 첨가 없이 아래 과정 그대로 사용할 것
                        
                        🍫 1. 솔방울 케이크
                        재료:
                        
                        몽쉘 1개
                        
                        초코 시리얼
                        
                        만드는 순서:
                        
                        몽쉘을 손으로 주물러 으깬다.
                        
                        손으로 타원형 또는 동그란 모양을 만든다.
                        
                        초코 시리얼을 콕콕 꽂아서 꾸민다.
                        
                        접시에 담아 완성한다.
                        
                        🍌 2. 바나나 식빵 롤
                        재료:
                        
                        식빵 1장 (가장자리 제거)
                        
                        바나나 1/2개
                        
                        땅콩버터 약간
                        
                        만드는 순서:
                        
                        식빵의 가장자리를 손으로 제거한다.
                        
                        식빵을 손으로 눌러 납작하게 만든다.
                        
                        땅콩버터를 바른다.
                        
                        바나나 반 개를 올린다.
                        
                        돌돌 말아 김밥처럼 만든다.
                        
                        플라스틱 빵칼로 먹기 좋게 썬다.
                        
                        🎨 3. 꿀호빵 꾸미기
                        재료:
                        
                        커스터드 빵 1개
                        
                        초코펜 1개
                        
                        엠앤엠즈 (또는 젤리, 초코볼 등)
                        
                        만드는 순서:
                        
                        커스터드 빵을 접시에 올린다.
                        
                        초코펜으로 얼굴이나 무늬를 그린다.
                        
                        엠앤엠즈로 눈, 코, 장식을 붙인다.
                        
                        꾸민 후 감상하고 맛있게 먹는다."""
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                max_tokens=500,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # API 응답에서 메시지 추출 (새로운 방식)
            ai_response = response.choices[0].message.content.strip()
            
            return JsonResponse({
                'response': ai_response,
                'status': 'success'
            })
            
        except Exception as e:
            # v1.0+에서는 에러 처리 방식이 변경됨
            error_message = str(e)
            logger.error(f"OpenAI API 오류: {error_message}")
            
            # API 키 문제인 경우 테스트용 응답 사용
            if "401" in error_message or "authentication" in error_message.lower() or "api_key" in error_message.lower():
                logger.warning("API 키 문제 발생, 테스트용 응답 사용")
                return chatbot_api_fallback_response(user_message)
            
            # 구체적인 에러 타입별 처리
            if "rate_limit" in error_message.lower() or "quota" in error_message.lower():
                response_msg = '현재 요청이 많아 잠시 후에 다시 시도해주세요.'
            else:
                response_msg = '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.'
            
            return JsonResponse({
                'response': response_msg,
                'status': 'error'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'response': '잘못된 요청 형식입니다.',
                'status': 'error'
            })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def chatbot_api_fallback_response(user_message):
    """API 키가 없거나 문제가 있을 때 사용할 테스트용 응답"""
    user_message = user_message.lower()
    
    # 간단한 테스트 응답
    if '안녕' in user_message:
        response_msg = "안녕하세요! 자무 AI 어시스턴트입니다 😊 (테스트 모드)"
    elif '자무' in user_message:
        response_msg = "자무는 건강에 좋은 특별한 차입니다! 어떤 것이 궁금하신가요? 🍵 (테스트 모드)"
    elif '주문' in user_message:
        response_msg = "자무 주문은 정말 간단해요! 원하시는 자무를 선택하시면 됩니다 📦 (테스트 모드)"
    elif '건강' in user_message:
        response_msg = "건강 관리는 정말 중요하죠! 자무가 많은 도움이 될 거예요 💪 (테스트 모드)"
    elif '효능' in user_message or '효과' in user_message:
        response_msg = "자무는 항산화, 면역력 강화, 스트레스 완화에 도움이 됩니다! ✨ (테스트 모드)"
    elif '가격' in user_message or '얼마' in user_message:
        response_msg = "자무의 가격은 종류에 따라 다릅니다. 자세한 정보는 주문 페이지를 확인해주세요! 💰 (테스트 모드)"
    else:
        import random
        responses = [
            "흥미로운 질문이네요! 자무에 대해 더 알고 싶으시면 언제든 말씀해주세요 ✨ (테스트 모드)",
            "네, 알겠습니다! 자무 관련해서 궁금한 것이 있으시면 언제든지 물어보세요 😊 (테스트 모드)",
            "좋은 질문입니다! 자무의 다양한 효능에 대해 더 자세히 알려드릴까요? 🌿 (테스트 모드)",
            "도움이 되었길 바라요! 자무 주문이나 다른 질문이 있으시면 말씀해주세요 🙌 (테스트 모드)"
        ]
        response_msg = random.choice(responses)
        
    return JsonResponse({
        'response': response_msg,
        'status': 'success'
    })

def order_status_api(request):
    """주문 상태 확인 API"""
    if request.method == 'GET':
        order_id = request.GET.get('order_id')
        
        # 주문 상태 확인 로직
        status = "processing"  # 실제 상태 확인 로직으로 대체
        
        return JsonResponse({
            'order_id': order_id,
            'status': status,
            'message': '주문이 처리 중입니다.'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)