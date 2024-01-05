#!/bin/bash

# 初始化计数器
total_cases=0
passed_cases=0
failed_cases=0

# 测试知乎
test_zhihu() {
    total_cases=$((total_cases + 1))
    echo "Testing Zhihu..."
    result=$(curl --location --request POST 'http://127.0.0.1:8001/v1/cralwer' \
        --header 'Authorization: Basic c2VjcmV0OmtleQ==' \
        --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
        --header 'Content-Type: application/json' \
        --data-raw '{"url": "https://zhuanlan.zhihu.com/p/671488335"}')
    check_result "Zhihu" "$result"
}

# 测试Bilibili
test_bilibili() {
    total_cases=$((total_cases + 1))
    echo "Testing Bilibili..."
    result=$(curl --location --request POST 'http://127.0.0.1:8001/v1/cralwer' \
        --header 'Authorization: Basic c2VjcmV0OmtleQ==' \
        --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
        --header 'Content-Type: application/json' \
        --data-raw '{"url": "https://www.bilibili.com/read/cv27369858/"}')
    check_result "Bilibili" "$result"
}

# 测试文章总结
test_summary() {
    total_cases=$((total_cases + 1))
    echo "Testing Summary..."
    result=$(curl --location --request POST 'http://127.0.0.1:8001/v1/summary' \
        --header 'Authorization: Basic c2VjcmV0OmtleQ==' \
        --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
        --header 'Content-Type: application/json' \
        --data-raw '{"documents": "ipsum irure ullamco"}')
    check_result "Summary" "$result"
}

# 测试文章QA
test_qa() {
    total_cases=$((total_cases + 1))
    echo "Testing QA..."
    result=$(curl --location --request POST 'http://127.0.0.1:8001/v1/qa' \
        --header 'Authorization: Basic c2VjcmV0OmtleQ==' \
        --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "question": "请问Deepread是什么？",
            "context": "用批阅奏章的方式阅读文章"
        }')
    check_result "QA" "$result"
}

# 测试内容审查接口
test_moderation() {
    total_cases=$((total_cases + 1))
    echo "Testing Moderation..."
    result=$(curl --location --request POST 'http://127.0.0.1:8001/v1/moderation' \
        --header 'Authorization: Basic c2VjcmV0OmtleQ==' \
        --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "context": "I love u"
        }')
    check_result "Moderation" "$result"
}

# 测试检查服务器接口
test_health() {
    total_cases=$((total_cases + 1))
    echo "Testing Health..."
    result=$(curl --location --request GET 'http://127.0.0.1:8001/v1/health' \
        --header 'Authorization: Basic c2VjcmV0OmtleQ==' \
        --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)')
    check_result "Health" "$result"
}

# 检查测试结果
check_result() {
    service=$1
    result=$2

    if [[ "$result" == *"error"* || "$result" == *"failed"* || "$result" == *"null"* ]]; then
        echo "Test for $service failed: $result"
        failed_cases=$((failed_cases + 1))
    else
        echo "Test for $service passed: $result"
        passed_cases=$((passed_cases + 1))
    fi
}

# 执行测试
test_zhihu
test_bilibili
test_summary
test_qa
test_moderation
test_health

# 输出总案例数、通过案例数和不通过案例数
echo "Total cases: $total_cases"
echo "Passed cases: $passed_cases"
echo "Failed cases: $failed_cases"
