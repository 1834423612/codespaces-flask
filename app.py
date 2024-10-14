from flask import Flask, jsonify, render_template, request
import requests
import mysql.connector
import time
import json
import threading

app = Flask(__name__)

# MySQL数据库配置
db_config = {
    'user': 'QuestionBank',
    'password': '2jFkTxYRy3mXDkNb',
    'host': '43.153.100.17',
    'database': 'QuestionBank'
}

# 线程控制变量
fetch_thread = None
fetching = False

# 更新映射表名，以便于处理各类型问题
table_mapping = {
    'SAT_English': 'SAT_English',
    'SAT_Math': 'SAT_Math',
    'PSAT10_English': 'PSAT10_English',
    'PSAT10_Math': 'PSAT10_Math',
    'PSAT8_9_English': 'PSAT8_9_English',
    'PSAT8_9_Math': 'PSAT8_9_Math'
}

# 存储日志信息
log_messages = []  # 添加一个全局列表来保存日志

def log_message(message):
    """记录日志信息并保持仅最新的 N 条（如 N=100）"""
    log_messages.append(message)
    if len(log_messages) > 100:  # 限制存储的日志条目数
        log_messages.pop(0)

def is_question_exist(external_id, table_name):
    """检查数据库中是否已存在该题目"""
    if table_name is None:
        return False  # 如果没有表名则返回 False
    
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    check_query = f"SELECT COUNT(*) FROM {table_name} WHERE external_id = %s"
    cursor.execute(check_query, (external_id,))
    result = cursor.fetchone()[0]  # 获取计数结果

    cursor.close()
    cnx.close()
    
    return result > 0  # 如果存在，返回 True

def fetch_all_questions(test_id, domain):
    """获取所有问题的 ID 列表"""
    url = "https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-questions"
    body = {
        "asmtEventId": test_id,
        "test": 1,  # 1 for English, 2 for Math
        "domain": domain
    }
    print(f"🔎 Fetching questions from {url} with body: {body}")  # Debug output

    response = requests.post(url, json=body)
    return response.json() if response.status_code == 200 else [] 

def fetch_question_detail(external_id):
    """根据外部 ID 获取题目的详细信息"""
    if external_id is None:
        print(f"⚠️ No external_id provided for detail fetch.")
        return None  
    
    url = "https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-question"
    body = {"external_id": external_id}
    print(f"🔄 Fetching question detail from {url} with body: {body}")  
    response = requests.post(url, json=body)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch details for external_id '{external_id}', status code: {response.status_code}, response: {response.text}")
        return None  
    
def convert_to_external_id_format(math_details):
    # 确保验证 `math_details` 的结构
    try:
        item = math_details[0]  # 确保至少有一个条目
        if 'item_id' in item and 'answer' in item:
            # 获取选项并转换结构
            choices = item['answer'].get('choices', {})
            answer_options = [
                {"content": choice['body'].replace("\u003Cp class=\"choice_paragraph \">", "").replace("</p>", "")}
                for choice in choices.values()
            ]

            return {
                "keys": [item['item_id']],
                "ibn": item['ibn'],  # 插入 ibn 来处理数据库
                "rationale": item['answer'].get('rationale', ''),
                "stem": item.get('prompt', ''),
                "answerOptions": answer_options,  # 插入转换后的 sélection
                "correct_answer": [item['answer'].get('correct_choice', '')]
            }
        else:
            log_message(f"❌ Missing expected fields in math details: {item}")
            return None  # 如果数据结构不符合预期则返回 None
    except Exception as e:
        log_message(f"❌ Error converting math details: {str(e)}")
        return None  # 返回 None 以在插入时跳过该问题


def fetch_questions(test_selection):
    global fetching
    fetching = True
    current_status = ""

    tests = {
        'SAT_English': (99, "INI,CAS,EOI,SEC"),
        'SAT_Math': (99, "H,P,Q,S"),
        'PSAT10_English': (100, "INI,CAS,EOI,SEC"),
        'PSAT10_Math': (100, "H,P,Q,S"),
        'PSAT8_9_English': (102, "INI,CAS,EOI,SEC"),
        'PSAT8_9_Math': (102, "H,P,Q,S"),
    }

    if test_selection in tests:
        test_id, domain = tests[test_selection]
        questions = fetch_all_questions(test_id, domain)

        total_questions = len(questions)
        processed_questions = 0

        for question in questions:
            if not fetching:
                log_message(f"🛑 Fetch operation terminated.")
                break

            question['test_selection'] = test_selection
            
            if test_selection.endswith('Math'):
                # Process Math questions
                if question['ibn']:
                    # Fetch details for ibn
                    response = requests.get(f"https://saic.collegeboard.org/disclosed/{question['ibn']}.json")
                    
                    if response.status_code == 200:
                        math_details = response.json()
                        if math_details and len(math_details) > 0:
                            # If returned data is valid, convert to external_id format
                            detailed_question = convert_to_external_id_format(math_details)
                            if detailed_question is None:
                                log_message(f"❌ Conversion to external ID format failed for ibn: {question['ibn']}")
                                continue
                        else:
                            log_message(f"❌ No data returned for ibn: {question['ibn']}")
                            continue
                    else:
                        log_message(f"❌ Failed to fetch details for ibn: {question['ibn']}, status code: {response.status_code}")
                        continue
                elif question['external_id']:
                    # Load from external_id normally
                    detailed_question = fetch_question_detail(question['external_id'])
                else:
                    log_message(f"❌ Missing both ibn and external_id for question.")
                    continue
            else:
                detailed_question = fetch_question_detail(question['external_id'])

            log_message(f"Fetched detailed question for external_id: {question['external_id']}")
            # Ensure detailed_question is not None and insert to DB
            if detailed_question:
                insert_question_to_db(question, detailed_question, test_selection)

            processed_questions += 1
            current_status = f"已处理 {processed_questions}/{total_questions} 个问题..."
            log_message(current_status)

            time.sleep(0.2)

        log_message(f"🟡 Completed fetch for '{test_selection}'.")
    else:
        log_message(f"❗ Invalid test selection '{test_selection}'.")

    fetching = False 

def insert_question_to_db(question, detailed_question, test_selection):
    """插入问题到数据库"""
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # 从选择中获取学科
    table_name = table_mapping.get(test_selection)

    if table_name is None:
        print(f"❌ Invalid table name for '{test_selection}'.")
        cursor.close()
        cnx.close()
        return

    # 验证题目是否已存在
    if is_question_exist(question['external_id'], table_name):
        print(f"✅ Question with external_id '{question['external_id']}' already exists in '{table_name}'. Skipping...")
        cursor.close()
        cnx.close()
        return  # 如果已存在，跳过插入

    insert_query = f"""
    INSERT INTO {table_name} (question_id, skill_cd, skill_desc, difficulty, external_id, ibn, rationale, stem, stimulus, answerOptions, correct_answer)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # 如果详细问题是 None，设置默认插入空值
    if detailed_question is None:
        detailed_question = {
            'rationale': '',
            'stem': '',
            'stimulus': '',
            'answerOptions': [],
            'correct_answer': []  
        }

    # 提取 skill_cd 和 skill_desc
    skill_cd = detailed_question.get('skill_cd', '')
    skill_desc = detailed_question.get('skill_desc', '')

    # 检查获取的字段值，确保每个值都有内容
    question_id = detailed_question.get('keys', [None])[0]
    difficulty = detailed_question.get('difficulty', 'E')  # 假设难度为 'E'

    if question_id is None:
        print(f"❌ Missing 'question_id' for external_id '{question['external_id']}'. Inserting failed...")
        cursor.close()
        cnx.close()
        return

    # 插入数据
    cursor.execute(insert_query, (
        question_id,  # question_id
        skill_cd,     # skill_cd
        skill_desc,   # skill_desc
        difficulty,   # difficulty
        question['external_id'], 
        detailed_question.get("ibn", ""),  # 这里插入 ibn
        detailed_question.get("rationale", ""), 
        detailed_question.get("stem", ""),
        detailed_question.get("stimulus", ""),
        json.dumps(detailed_question.get("answerOptions", [])),  
        json.dumps(detailed_question.get("correct_answer", []))  # 如果确实有该字段
    ))

    cnx.commit()
    cursor.close()
    cnx.close()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_logs', methods=['GET'])
def get_logs():
    """获取日志信息"""
    return jsonify({"logs": log_messages}), 200

@app.route('/begin_fetch', methods=['POST'])
def begin_fetch():
    global fetch_thread

    test_selection = request.form.get('test_selection')
    
    if fetch_thread and fetch_thread.is_alive():
        return jsonify({"status": "正在进行获取操作，请稍后再试。"}), 400

    fetch_thread = threading.Thread(target=fetch_questions, args=(test_selection,))
    fetch_thread.start()
    
    return jsonify({"status": "获取操作已启动。"}), 200

@app.route('/stop_fetch', methods=['POST'])
def stop_fetch():
    global fetching
    fetching = False
    return jsonify({"status": "获取操作已终止。"}), 200

@app.route('/current_status', methods=['GET'])
def current_status():
    """返回当前状态"""
    return jsonify({"status": "正在进行中..." if fetching else "尚未开始."}), 200

if __name__ == '__main__':
    app.run(debug=True)