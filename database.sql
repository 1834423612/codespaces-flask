-- 创建表用于 SAT 英语题目
CREATE TABLE SAT_English (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id VARCHAR(255) NOT NULL,
    skill_cd VARCHAR(255) NOT NULL,
    skill_desc VARCHAR(255) NOT NULL,
    difficulty ENUM('E', 'M', 'H') NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    rationale TEXT,  -- 解析
    stem TEXT,      -- 题干
    stimulus TEXT,  -- 背景信息
    answerOptions JSON,  -- 答案选项，存储为 JSON 格式
    correct_answer JSON,  -- 正确答案
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建表用于 SAT 数学题目
CREATE TABLE SAT_Math (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id VARCHAR(255) NOT NULL,
    skill_cd VARCHAR(255) NOT NULL,
    skill_desc VARCHAR(255) NOT NULL,
    difficulty ENUM('E', 'M', 'H') NOT NULL,
    external_id VARCHAR(255),
    ibn VARCHAR(255),  -- 数学题目特定标识
    rationale TEXT,  -- 解析
    stem TEXT,      -- 题干
    stimulus TEXT,  -- 背景信息
    answerOptions JSON,  -- 答案选项，存储为 JSON 格式
    correct_answer JSON,  -- 正确答案
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建表用于 PSAT10 英语题目
CREATE TABLE PSAT10_English (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id VARCHAR(255) NOT NULL,
    skill_cd VARCHAR(255) NOT NULL,
    skill_desc VARCHAR(255) NOT NULL,
    difficulty ENUM('E', 'M', 'H') NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    rationale TEXT,  -- 解析
    stem TEXT,      -- 题干
    stimulus TEXT,  -- 背景信息
    answerOptions JSON,  -- 答案选项，存储为 JSON 格式
    correct_answer JSON,  -- 正确答案
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建表用于 PSAT10 数学题目
CREATE TABLE PSAT10_Math (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id VARCHAR(255) NOT NULL,
    skill_cd VARCHAR(255) NOT NULL,
    skill_desc VARCHAR(255) NOT NULL,
    difficulty ENUM('E', 'M', 'H') NOT NULL,
    external_id VARCHAR(255),
    ibn VARCHAR(255),  -- 数学题目特定标识
    rationale TEXT,  -- 解析
    stem TEXT,      -- 题干
    stimulus TEXT,  -- 背景信息
    answerOptions JSON,  -- 答案选项，存储为 JSON 格式
    correct_answer JSON,  -- 正确答案
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建表用于 PSAT8/9 英语题目
CREATE TABLE PSAT8_9_English (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id VARCHAR(255) NOT NULL,
    skill_cd VARCHAR(255) NOT NULL,
    skill_desc VARCHAR(255) NOT NULL,
    difficulty ENUM('E', 'M', 'H') NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    rationale TEXT,  -- 解析
    stem TEXT,      -- 题干
    stimulus TEXT,  -- 背景信息
    answerOptions JSON,  -- 答案选项，存储为 JSON 格式
    correct_answer JSON,  -- 正确答案
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建表用于 PSAT8/9 数学题目
CREATE TABLE PSAT8_9_Math (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id VARCHAR(255) NOT NULL,
    skill_cd VARCHAR(255) NOT NULL,
    skill_desc VARCHAR(255) NOT NULL,
    difficulty ENUM('E', 'M', 'H') NOT NULL,
    external_id VARCHAR(255),
    ibn VARCHAR(255),  -- 数学题目特定标识
    rationale TEXT,  -- 解析
    stem TEXT,      -- 题干
    stimulus TEXT,  -- 背景信息
    answerOptions JSON,  -- 答案选项，存储为 JSON 格式
    correct_answer JSON,  -- 正确答案
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);